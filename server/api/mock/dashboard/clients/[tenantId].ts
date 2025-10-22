export default defineEventHandler(async (event) => {
  const tenantId = getRouterParam(event, 'tenantId')
  
  // Datos mock para clientes
  const mockClients = [
    {
      id: "client-1",
      name: "Juan Pérez",
      email: "juan.perez@email.com",
      phone: "+54 9 223 123-4567",
      status: "activo"
    },
    {
      id: "client-2", 
      name: "María González",
      email: "maria.gonzalez@email.com",
      phone: "+54 9 223 987-6543",
      status: "activo"
    },
    {
      id: "client-3",
      name: "Carlos Rodríguez", 
      email: "carlos.rodriguez@email.com",
      phone: "+54 9 223 555-1234",
      status: "activo"
    }
  ]
  
  return mockClients
})
