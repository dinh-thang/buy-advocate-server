## on creating a new project
1. load the configured filters for a default site type (children)
2. user can't change their site type (they will be prompt to create a new project if select a different site type)
3. load the set of filter and create a new record in the user_filter table, this is a must.


## on changing the site type (optional)
1. (not sure yet) there are 2 options, the user can still change the site type or they must to create a new project
2. if they can change the site type in place, load the new filter config and update in the user_filter table.


## on loading existing project
1. load existing configuration from the user_filters table, not through default filter table. For all existing project, this is a must.

## endpoint list
1. POST /api/projects/: create a new project using preset filter data (use filters table).
- site_type_id is default to childcare
- load the default filters
- this also set the user_filters field to the filter data

2. PATCH /api/projects/{project_id}: update the user_filters field if any filter is adjusted, maybe could be project name.
- (need clarify) if site type is updated, set the user_filters to the preset filters


3. GET /api/projects/{id}: get an existing project data (use user_filters table)
4. GET /api/projects/: get all projects of a user (should return only name and id)


5. (in consideration) GET /api/properties/(filters): get all the properties for a project's filters