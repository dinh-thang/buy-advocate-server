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

logger = logging.getLogger(__name__)

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

    logger.info(f"Applying min-max filter to {db_column_name}")
    logger.info(f"Filter data: {filter_data}")
    logger.info(f"Min value: {min_value}, Max value: {max_value}")
    
    try:
        if min_value is not None:
            query = query.gte(db_column_name, min_value)
            logger.info(f"Added gte filter: {db_column_name} >= {min_value}")
        if max_value is not None:
            query = query.lte(db_column_name, max_value)
            logger.info(f"Added lte filter: {db_column_name} <= {max_value}")
        
        # Log the current query state (this might not show the full SQL but helps with debugging)
        logger.info(f"Query object after applying {db_column_name} filter: {query}")
        
    except Exception as e:
        logger.error(f"Error applying min-max filter to {db_column_name}: {e}")
        logger.error(f"This might indicate the column doesn't exist or has incompatible data type")
        # Return the original query if filtering fails
        
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
    
    logger.info(f"Applying single value filter to {db_column_name}")
    logger.info(f"Filter data: {filter_data}")
    logger.info(f"Values to filter: {values}")
    
    if not values:
        logger.info("No values provided, returning original query")
        return query
    
    # Check if we're dealing with an array column (zones)
    if db_column_name == 'zones':
        # For array columns, use the @> operator to check if array contains ALL specified values
        # This will match records that contain ALL of the specified values
        query = query.contains(db_column_name, values)
        logger.info(f"Added contains filter for zones: {values}")
    else:
        # For text columns, use ilike for case-insensitive comparison
        for value in values:
            query = query.ilike(db_column_name, f'%{value}%')
            logger.info(f"Added ilike filter: {db_column_name} LIKE '%{value}%'")
        
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
    logger.info(f"Applying exact match filter to {db_column_name}")
    logger.info(f"Filter value: {filter_value}")
    
    if not filter_value:
        logger.info("No filter value provided, returning original query")
        return query
    
    try:
        # Handle comma-separated values as OR conditions (like "for-sale, for-lease")
        # This means we want records that match EXACTLY "for-sale" OR EXACTLY "for-lease"
        if "," in filter_value:
            values = [v.strip() for v in filter_value.split(",")]
            # Use 'in' operator for multiple exact values (OR logic)
            query = query.in_(db_column_name, values)
            logger.info(f"Added exact match 'in' filter: {db_column_name} IN {values}")
        else:
            # Single exact match
            query = query.eq(db_column_name, filter_value)
            logger.info(f"Added exact match filter: {db_column_name} = '{filter_value}'")
        
    except Exception as e:
        logger.error(f"Error applying exact match filter to {db_column_name}: {e}")
        # Return the original query if filtering fails
        
    return query 
