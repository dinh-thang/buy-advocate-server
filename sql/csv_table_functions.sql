-- Function to create a table with the CSV schema
-- This function needs to be created in Supabase Dashboard or via SQL Editor

CREATE OR REPLACE FUNCTION create_csv_table(p_table_name text)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Validate table name to prevent SQL injection
    IF p_table_name !~ '^[a-zA-Z_][a-zA-Z0-9_]*$' THEN
        RAISE EXCEPTION 'Invalid table name: %', p_table_name;
    END IF;
    
    -- Check if table already exists
    IF EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = p_table_name
    ) THEN
        RAISE EXCEPTION 'Table % already exists', p_table_name;
    END IF;
    
    -- Create the table with the required schema
    EXECUTE format('
        CREATE TABLE %I (
            id BIGINT PRIMARY KEY,
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            business_name TEXT NOT NULL
        )', p_table_name);
    
    -- Enable RLS (Row Level Security) for the new table
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', p_table_name);
    
    -- Create RLS policy for full access
    EXECUTE format('
        CREATE POLICY "Enable full access" ON %I
        FOR ALL
        TO authenticated
        USING (true)
        WITH CHECK (true)
    ', p_table_name);
    
    -- Grant permissions (adjust as needed based on your RLS policies)
    EXECUTE format('GRANT ALL ON TABLE %I TO authenticated', p_table_name);
    EXECUTE format('GRANT ALL ON TABLE %I TO service_role', p_table_name);
    
    RETURN format('Table %s created successfully', p_table_name);
END;
$$;

-- Function to drop a table (for cleanup purposes)
CREATE OR REPLACE FUNCTION drop_table(p_table_name text)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Validate table name to prevent SQL injection
    IF p_table_name !~ '^[a-zA-Z_][a-zA-Z0-9_]*$' THEN
        RAISE EXCEPTION 'Invalid table name: %', p_table_name;
    END IF;
    
    -- Check if table exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = p_table_name
    ) THEN
        RAISE EXCEPTION 'Table % does not exist', p_table_name;
    END IF;
    
    -- Drop the table
    EXECUTE format('DROP TABLE %I', p_table_name);
    
    RETURN format('Table %s dropped successfully', p_table_name);
END;
$$;

-- Function to ensure RLS policies are set up correctly for a table
CREATE OR REPLACE FUNCTION setup_table_policies(p_table_name text)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Validate table name to prevent SQL injection
    IF p_table_name !~ '^[a-zA-Z_][a-zA-Z0-9_]*$' THEN
        RAISE EXCEPTION 'Invalid table name: %', p_table_name;
    END IF;
    
    -- Check if table exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = p_table_name
    ) THEN
        RAISE EXCEPTION 'Table % does not exist', p_table_name;
    END IF;

    -- Enable RLS (Row Level Security) for the table
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', p_table_name);
    
    -- Drop existing policies if they exist
    BEGIN
        EXECUTE format('DROP POLICY IF EXISTS "Enable full access" ON %I', p_table_name);
    EXCEPTION WHEN OTHERS THEN
        -- Ignore errors from non-existent policies
        NULL;
    END;
    
    -- Create RLS policy for full access
    EXECUTE format('
        CREATE POLICY "Enable full access" ON %I
        FOR ALL
        TO authenticated
        USING (true)
        WITH CHECK (true)
    ', p_table_name);
    
    -- Grant permissions
    EXECUTE format('GRANT ALL ON TABLE %I TO authenticated', p_table_name);
    EXECUTE format('GRANT ALL ON TABLE %I TO service_role', p_table_name);
    
    RETURN format('Policies set up successfully for table %s', p_table_name);
END;
$$;

-- Function to set up RLS policies for anon read access
CREATE OR REPLACE FUNCTION setup_anon_read_policies(p_table_name text)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Validate table name to prevent SQL injection
    IF p_table_name !~ '^[a-zA-Z_][a-zA-Z0-9_]*$' THEN
        RAISE EXCEPTION 'Invalid table name: %', p_table_name;
    END IF;
    
    -- Check if table exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = p_table_name
    ) THEN
        RAISE EXCEPTION 'Table % does not exist', p_table_name;
    END IF;

    -- Enable RLS (Row Level Security) for the table
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', p_table_name);
    
    -- Drop existing policies if they exist
    BEGIN
        EXECUTE format('DROP POLICY IF EXISTS "Enable read access for anon" ON %I', p_table_name);
        EXECUTE format('DROP POLICY IF EXISTS "Enable all access for service role" ON %I', p_table_name);
    EXCEPTION WHEN OTHERS THEN
        NULL;
    END;
    
    -- Create RLS policy for anon read access
    EXECUTE format('
        CREATE POLICY "Enable read access for anon" ON %I
        FOR SELECT
        TO anon
        USING (true)
    ', p_table_name);

    -- Create RLS policy for service role full access
    EXECUTE format('
        CREATE POLICY "Enable all access for service role" ON %I
        FOR ALL
        TO service_role
        USING (true)
        WITH CHECK (true)
    ', p_table_name);
    
    -- Grant permissions
    EXECUTE format('GRANT SELECT ON TABLE %I TO anon', p_table_name);
    EXECUTE format('GRANT ALL ON TABLE %I TO service_role', p_table_name);
    
    RETURN format('Anon read policies set up successfully for table %s', p_table_name);
END;
$$;

-- Grant execute permissions on the functions
GRANT EXECUTE ON FUNCTION create_csv_table(text) TO authenticated;
GRANT EXECUTE ON FUNCTION create_csv_table(text) TO service_role;
GRANT EXECUTE ON FUNCTION drop_table(text) TO authenticated;
GRANT EXECUTE ON FUNCTION drop_table(text) TO service_role;
GRANT EXECUTE ON FUNCTION setup_table_policies(text) TO authenticated;
GRANT EXECUTE ON FUNCTION setup_table_policies(text) TO service_role;
GRANT EXECUTE ON FUNCTION setup_anon_read_policies(text) TO service_role; 