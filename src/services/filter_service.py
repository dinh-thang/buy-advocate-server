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
    if min_value is not None:
        query = query.gte(db_column_name, min_value)
    if max_value is not None:
        query = query.lte(db_column_name, max_value)
    return query 