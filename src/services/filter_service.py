"""
MISSING FILTERS FOR:
- Distance to POIs (need clarification on the filter's format)
- Childcare demand ratio catchment
- Planning permits catchment
- Overlays (maybe multiple select filter)
- Corner (maybe single select filter)
- Frontage (maybe a range filter)
- Yield percentage (maybe a range filter)
- Lease term (this is a text field, need clarification)
- Rent per annum (maybe a range filter)
"""

import logging
from postgrest.exceptions import APIError

logger = logging.getLogger(__name__)


def is_column_not_exist_error(e: Exception) -> bool:
    """
    Check if the error is due to a non-existent column
    """
    if isinstance(e, APIError):
        error_message = getattr(e, 'message', '').lower()
        return 'column' in error_message and 'does not exist' in error_message
    return False


def apply_min_max_filter(query, db_column_name, filter_data):
    """
    Applies a min-max filter to a Supabase query.
    :param query: The Supabase query object
    :param db_column_name: The column name to filter on
    :param filter_data: Dict with 'min' and/or 'max' keys
    :return: Modified query object
    """
    min_value = filter_data.get('min')
    max_value = filter_data.get('max')
    
    try:
        if min_value is not None:
            query = query.gte(db_column_name, min_value)
        if max_value is not None:
            query = query.lte(db_column_name, max_value)
        
        logger.info(f"✅ Applied range filter: {db_column_name} [{min_value}-{max_value}]")
        
    except Exception as e:
        if is_column_not_exist_error(e):
            logger.warning(f"⚠️ Skipping filter for non-existent column: {db_column_name}")
            return query
        logger.error(f"❌ Error applying range filter to {db_column_name}: {e}")
        
    return query


def apply_zone_filter(query, db_column_name, filter_data):
    """
    Applies a zone filter to a Supabase query for array columns.
    Matches records that contain ANY of the specified values in the array.
    :param query: The Supabase query object
    :param db_column_name: The column name to filter on (should be an array column)
    :param filter_data: Dict with 'values' key containing list of zone values
    :return: Modified query object
    """
    values = filter_data.get('values', []) if isinstance(filter_data, dict) else []
    
    if not values:
        logger.info(f"⚠️ No zone values provided for {db_column_name}")
        return query
    
    try:
        # Use the overlap operator (&&) to check if the array contains ANY of the specified values
        query = query.overlaps(db_column_name, values)
        logger.info(f"✅ Applied zone filter: {db_column_name} overlaps {values}")
        
    except Exception as e:
        if is_column_not_exist_error(e):
            logger.warning(f"⚠️ Skipping filter for non-existent column: {db_column_name}")
            return query
        logger.error(f"❌ Error applying zone filter to {db_column_name}: {e}")
        
    return query


def apply_single_value_filter(query, db_column_name, filter_data):
    """
    Applies a single value filter to a Supabase query.
    For array columns, checks if ALL of the specified values exist in the array.
    For text columns, performs case-insensitive comparison.
    :param query: The Supabase query object
    :param db_column_name: The column name to filter on
    :param filter_data: Dict with 'values' key containing list of values
    :return: Modified query object
    """
    values = filter_data.get('values', []) if isinstance(filter_data, dict) else []
    
    if not values:
        logger.info(f"⚠️ No values provided for {db_column_name}")
        return query
    
    try:
        # Check if we're dealing with an array column (zones)
        if db_column_name == 'zones':
            query = query.contains(db_column_name, values)
            logger.info(f"✅ Applied array contains filter: {db_column_name} contains {values}")
        else:
            # For text columns, use ilike for case-insensitive comparison
            for value in values:
                query = query.ilike(db_column_name, f'%{value}%')
            logger.info(f"✅ Applied text filter: {db_column_name} LIKE {values}")
        
    except Exception as e:
        if is_column_not_exist_error(e):
            logger.warning(f"⚠️ Skipping filter for non-existent column: {db_column_name}")
            return query
        logger.error(f"❌ Error applying single value filter to {db_column_name}: {e}")
        
    return query 


def apply_exact_match_filter(query, db_column_name, filter_value):
    """
    Applies an exact match filter to a Supabase query.
    For market status filtering on category column.
    This performs strict exact matching - "for-sale" will NOT match "for-sale, for-lease".
    :param query: The Supabase query object
    :param db_column_name: The column name to filter on
    :param filter_value: The exact value to match (can contain comma-separated values for OR logic)
    :return: Modified query object
    """
    if not filter_value:
        logger.info(f"⚠️ No filter value provided for {db_column_name}")
        return query
    
    try:
        # Handle comma-separated values as OR conditions (like "for-sale, for-lease")
        if "," in filter_value:
            values = [v.strip() for v in filter_value.split(",")]
            query = query.in_(db_column_name, values)
            logger.info(f"✅ Applied exact match filter: {db_column_name} IN {values}")
        else:
            query = query.eq(db_column_name, filter_value)
            logger.info(f"✅ Applied exact match filter: {db_column_name} = '{filter_value}'")
        
    except Exception as e:
        if is_column_not_exist_error(e):
            logger.warning(f"⚠️ Skipping filter for non-existent column: {db_column_name}")
            return query
        logger.error(f"❌ Error applying exact match filter to {db_column_name}: {e}")
        
    return query 


"""
filter_data format:
{
    'values': [
        {'db_column_name': 'distance_to_primary', 'value': 1, 'isCloserTo': True},
        {'db_column_name': 'distance_to_train', 'value': 1.2, 'isCloserTo': True},
    ]
}
"""
def apply_distance_to_poi_filter(query, filter_data):
    """
    Applies a distance to POI filter to a Supabase query.
    :param query: The Supabase query object
    :param filter_data: Dict with 'values' key containing list of filters, each with 'db_column_name', 'value', and 'isCloserTo'
    :return: Modified query object
    """
    filters = filter_data.get('values', [])
    
    if not filters:
        logger.info("⚠️ No distance to POI filters provided")
        return query
    
    try:
        applied_filters = []
        for filter_item in filters:
            column = filter_item.get('db_column_name')
            threshold = filter_item.get('value')
            is_closer_to = filter_item.get('isCloserTo', True)
            
            if not column or threshold is None:
                logger.warning(f"⚠️ Skipping invalid POI filter: {filter_item}")
                continue
            
            try:
                # Filter out records where distance is 0 (invalid data)
                query = query.not_.eq(column, 0)
                
                if is_closer_to:
                    query = query.lte(column, threshold)
                    applied_filters.append(f"{column} ≤ {threshold}km")
                else:
                    query = query.gte(column, threshold)
                    applied_filters.append(f"{column} ≥ {threshold}km")
                    
            except Exception as e:
                if is_column_not_exist_error(e):
                    logger.warning(f"⚠️ Skipping filter for non-existent column: {column}")
                    continue
                logger.error(f"❌ Error applying distance filter to {column}: {e}")
                continue
        
        if applied_filters:
            logger.info(f"✅ Applied distance to POI filters: {', '.join(applied_filters)}")
        
    except Exception as e:
        logger.error(f"❌ Error applying distance to POI filters: {e}")
        
    return query


"""
filter_data format:
{
    'is_higher_than': True,
    'value': 0.5,
}
"""
def apply_supply_demand_ratio_filter(query, db_column_name, filter_data):
    """
    Applies a supply demand ratio filter to a Supabase query.
    :param query: The Supabase query object
    :param db_column_name: The column name to filter on
    :param filter_data: Dict with 'is_higher_than' key, 'value' key
    :return: Modified query object
    """
    is_higher_than = filter_data.get('is_higher_than')
    value = filter_data.get('value')
    
    if value is None:
        logger.info(f"⚠️ No value provided for {db_column_name}")
        return query
    
    try:
        if is_higher_than:
            query = query.gte(db_column_name, value)
            logger.info(f"✅ Applied ratio filter: {db_column_name} ≥ {value}")
        else:
            query = query.lte(db_column_name, value)
            logger.info(f"✅ Applied ratio filter: {db_column_name} ≤ {value}")
            
    except Exception as e:
        if is_column_not_exist_error(e):
            logger.warning(f"⚠️ Skipping filter for non-existent column: {db_column_name}")
            return query
        logger.error(f"❌ Error applying ratio filter to {db_column_name}: {e}")
        
    return query


