// middleware/auth.global.ts

// Define a type for our user profile for better type safety
type Profile = {
  role: 'realtor' | 'client' | 'admin';
  full_name: string | null;
};

export default defineNuxtRouteMiddleware(async (to, from) => {
  // We don't want the middleware to run on server-side rendering, only on client-side navigation.
  // if (process.server) {
  //   return;
  // }

  // const user = useSupabaseUser();
  // const client = useSupabaseClient();

  // // Define routes that are protected and role-specific
  // const realtorRoutes = ['/realtor/profile'];
  // const clientRoutes = ['/client/profile'];

  // // Combine all protected routes
  // const protectedRoutes = [...realtorRoutes, ...clientRoutes];

  // // If the user tries to access a protected route without being logged in,
  // // redirect them to the homepage to trigger the login modal.
  // if (!user.value && protectedRoutes.includes(to.path)) {
  //   console.log('Middleware: User not logged in, redirecting to home.');
  //   return navigateTo('/');
  // }

  // // If the user is logged in, perform role checks and redirection for incomplete profiles.
  // if (user.value) {
  //   // Fetch the user's profile from the database to get their role and check for completion.
  //   const { data: profile, error } = await client
  //     .from('profiles')
  //     .select('role, full_name')
  //     .eq('id', user.value.id)
  //     .single<Profile>();

  //   // Handle cases where the profile couldn't be fetched.
  //   if (error || !profile) {
  //     console.error('Middleware: Error fetching profile or profile not found.', error);
  //     // If we are already on the homepage, do nothing to avoid an infinite redirect loop.
  //     if (to.path === '/') {
  //       return; 
  //     }
  //     // For any other page, redirecting to home is a safe default.
  //     return navigateTo('/');
  //   }

  //   const userRole = profile.role;
  //   const isProfileIncomplete = !profile.full_name; // A simple check for now.

  //   // --- Role-Based Route Protection ---
  //   // Prevent clients from accessing realtor routes.
  //   if (userRole !== 'realtor' && realtorRoutes.some(route => to.path.startsWith(route))) {
  //     console.log(`Middleware: Client/other role attempting to access realtor route. Redirecting.`);
  //     return navigateTo('/'); // Or to a dedicated '/unauthorized' page.
  //   }
  //   // Prevent realtors from accessing client routes.
  //   if (userRole !== 'client' && clientRoutes.some(route => to.path.startsWith(route))) {
  //     console.log(`Middleware: Realtor/other role attempting to access client route. Redirecting.`);
  //     return navigateTo('/'); // Or to a dedicated '/unauthorized' page.
  //   }

  //   // --- Incomplete Profile Redirection ---
  //   // If the profile is incomplete, redirect the user to their corresponding profile page
  //   // as long as they aren't already there.
  //   const targetProfilePage = `/${userRole}/profile`;
  //   if (isProfileIncomplete && to.path !== targetProfilePage) {
  //     console.log(`Middleware: Profile incomplete, redirecting to ${targetProfilePage}.`);
  //     return navigateTo(targetProfilePage);
  //   }
  // }
}); 