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

    print(f"Applying min-max filter to {db_column_name} with values: min={min_value}, max={max_value}")
    
    if min_value is not None:
        query = query.gte(db_column_name, min_value)
    if max_value is not None:
        query = query.lte(db_column_name, max_value)
    return query 


def apply_zone_filter(query, db_column_name, filter_data):
    """
    Applies a zone filter to a Supabase query.
    :param query: The Supabase query object
    :param db_column_name: The column name to filter on (zones)
    :param filter_data: Dict with 'zones' key containing list of zone strings
    :return: Modified query object
    """
    zones = filter_data.get('zones', [])
    
    if not zones:
        return query
        
    print(f"Applying zone filter to {db_column_name} with zones: {zones}")
    
    # For each zone in the input list, check if it exists in the database column
    for zone in zones:
        # Use contains to check if the zone exists in the array
        query = query.contains(db_column_name, [zone])
        
    return query 


async def filter_by_zones(
    query,
    db_column_name,
    filter_data
):
    """
    Filters the Supabase query by zones.

    The database stores zones as strings like "{Z1, Z2, Z3}".
    The filter checks if any of the input zones are present in the column.

    :param query: Supabase query builder object.
    :param db_column_name: Name of the database column to filter (e.g. "zones").
    :param filter_data: Dict with 'zones' key containing a list of zone strings (case-insensitive).
    :return: Modified query builder with the zones filter applied.
    """

    zones = filter_data.get("zones")
    if not zones:
        # No zones filter provided, return original query unmodified
        return query

    # Normalize input zones (uppercase) to match DB format (e.g. Z1)
    normalized_zones = [zone.upper() for zone in zones]

    # Build a list of filter conditions
    # Since zones column format is like '{Z1, Z2}', we can use Postgres text search operators.
    # One approach is to check if zones column contains the zone string (case-insensitive).
    # Using "ilike" with pattern '%Z1%' is simple but may cause false positives if zone codes overlap,
    # so we use the pattern with braces and commas for more exact match.
    # Pattern examples:
    # - zones ilike '%{Z1,%' OR zones ilike '%,Z1,%' OR zones ilike '%,Z1}%' OR zones ilike '{Z1}'

    # To simplify, use Postgres array operators if the column is stored as an array type.
    # If it's a string, we simulate array containment using text pattern matching.

    # For supabase PostgREST, we can use 'or' filters joined by commas.

    conditions = []
    for zone in normalized_zones:
        # Create patterns to cover:
        # - zone at start: "{ZONE,"
        # - zone at middle: ", ZONE,"
        # - zone at end: ", ZONE}"
        # - single zone: "{ZONE}"
        # Use ilike for case-insensitivity.
        patterns = [
            f"{{{zone},%",     # Start: "{Z1,"
            f"%, {zone},%",    # Middle: ", Z1,"
            f"%, {zone}}}",    # End: ", Z1}"
            f"{{{zone}}}"      # Single zone "{Z1}"
        ]
        for p in patterns:
            # Escape braces in pattern by wrapping with % and use ilike
            conditions.append(f"{db_column_name}.ilike.%{p}%")

    # Combine conditions with OR operator in PostgREST filter syntax
    # It expects comma-separated or expressions inside parentheses: or=(cond1,cond2,...)
    or_filter = ",".join(conditions)

    # Apply or filter to the query
    # Supabase client in python expects filters using 'or' like:
    # query = query.or_('zones.ilike.%{Z1}%,zones.ilike.%{Z2}%')
    # Since each condition is like zones.ilike.%pattern%, we join them by comma inside or_

    query = query.or_(or_filter)

    return query
