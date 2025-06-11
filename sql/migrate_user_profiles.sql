-- Migrate existing users to user_profile table
-- This script is idempotent (safe to run multiple times)

-- Insert profiles for users who don't have one yet
INSERT INTO public.user_profile (user_id)
SELECT au.id
FROM auth.users au
LEFT JOIN public.user_profile up ON up.user_id = au.id
WHERE up.id IS NULL;

-- Return count of migrated users
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN up.id IS NOT NULL THEN 1 ELSE 0 END) as users_with_profiles,
    COUNT(*) - SUM(CASE WHEN up.id IS NOT NULL THEN 1 ELSE 0 END) as users_without_profiles
FROM auth.users au
LEFT JOIN public.user_profile up ON up.user_id = au.id; 