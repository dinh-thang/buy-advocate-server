# CSV Table Upload Feature

This feature allows users to upload CSV files and automatically create corresponding tables in Supabase with a predefined schema.

## Setup Instructions

### 1. Create Supabase Functions

Before using the CSV upload feature, you need to create the required SQL functions in your Supabase database.

1. Open your Supabase Dashboard
2. Navigate to the SQL Editor
3. Execute the SQL code from `sql/csv_table_functions.sql`

This will create two functions:
- `create_csv_table(table_name)` - Creates a new table with the CSV schema
- `drop_table(table_name)` - Drops a table (used for cleanup on errors)

### 2. Required CSV Format

The CSV file must have exactly these 4 columns in this order:

```csv
id,latitude,longitude,business_name
1,-33.8688,151.2093,"Sydney Coffee Co"
2,-37.8136,144.9631,"Melbourne Bistro"
```

**Column Specifications:**
- `id` - Integer identifier (BIGINT)
- `latitude` - Decimal latitude between -90 and 90 (DOUBLE PRECISION)
- `longitude` - Decimal longitude between -180 and 180 (DOUBLE PRECISION)  
- `business_name` - Text business name (TEXT)

### 3. Table Naming Rules

Table names must:
- Start with a letter or underscore
- Contain only letters, numbers, and underscores
- Be unique (tables cannot be overwritten)

### 4. File Size Considerations

- The system processes files in batches of 1000 rows
- Large files (thousands of rows) are supported
- Files are processed entirely on the backend for security

## Usage

### Frontend Component

Import and use the `CsvTableUploader` component in your admin interface:

```tsx
import CsvTableUploader from '@/components/admin/csv-table-uploader';

function AdminPage() {
  return (
    <div>
      <CsvTableUploader />
    </div>
  );
}
```

### API Endpoint

The backend endpoint is available at:

```
POST /api/admin/upload-csv-table
```

**Parameters:**
- `file` (FormData) - CSV file
- `table_name` (string) - Name for the new table

**Response:**
```json
{
  "message": "Table 'my_locations' created successfully",
  "table_name": "my_locations", 
  "rows_processed": 1500
}
```

## Error Handling

The system handles various error scenarios:

1. **Invalid CSV format** - Missing or extra columns
2. **Table name conflicts** - Table already exists
3. **Invalid table names** - Non-alphanumeric characters
4. **File format issues** - Non-CSV files
5. **Batch insert failures** - Automatic cleanup of partially created tables

## Security Features

- Table names are validated against SQL injection
- Files are processed entirely on the backend
- Row Level Security (RLS) is enabled on created tables
- Proper database permissions are set

## Performance

- Batch processing in chunks of 1000 rows
- Parallel processing for large files
- Memory-efficient CSV parsing
- Automatic transaction rollback on failures

## Troubleshooting

### Common Issues

1. **Function not found error**
   - Ensure you've executed the SQL functions in Supabase
   - Check function permissions

2. **Permission denied**
   - Verify your Supabase service role has the correct permissions
   - Check RLS policies if accessing tables fails

3. **CSV parsing errors**
   - Ensure CSV has exactly 4 columns with correct names
   - Check for BOM encoding issues (UTF-8-BOM is supported)

4. **Table creation failures**
   - Verify table name follows naming rules
   - Check for existing tables with the same name

### Debugging

Check the server logs for detailed error messages. The system logs:
- Batch processing progress
- Table creation success/failure
- Detailed error information for troubleshooting 