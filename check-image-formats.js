// Script para verificar formatos de imagen en la API
async function checkImageFormats() {
  try {
    console.log('🔍 Verificando formatos de imagen en la API...');
    
    const response = await fetch('https://fapi.showtimeprop.com/properties/all');
    const properties = await response.json();
    
    console.log(`📊 Total de propiedades: ${properties.length}`);
    
    const imageFormats = {
      jpg: 0,
      jpeg: 0,
      png: 0,
      avif: 0,
      webp: 0,
      other: 0
    };
    
    let totalImages = 0;
    let propertiesWithImages = 0;
    
    properties.forEach((property, index) => {
      if (property.images && property.images.length > 0) {
        propertiesWithImages++;
        
        property.images.forEach(imageUrl => {
          totalImages++;
          const extension = imageUrl.split('.').pop().toLowerCase();
          
          if (extension.includes('jpg')) {
            imageFormats.jpg++;
          } else if (extension.includes('jpeg')) {
            imageFormats.jpeg++;
          } else if (extension.includes('png')) {
            imageFormats.png++;
          } else if (extension.includes('avif')) {
            imageFormats.avif++;
          } else if (extension.includes('webp')) {
            imageFormats.webp++;
          } else {
            imageFormats.other++;
          }
        });
        
        // Mostrar algunas URLs de ejemplo
        if (index < 3) {
          console.log(`\n📷 Propiedad ${index + 1} - ${property.images.length} imágenes:`);
          property.images.slice(0, 3).forEach((url, i) => {
            console.log(`  ${i + 1}. ${url}`);
          });
        }
      }
    });
    
    console.log('\n📈 RESUMEN DE FORMATOS:');
    console.log(`📊 Propiedades con imágenes: ${propertiesWithImages}`);
    console.log(`📊 Total de imágenes: ${totalImages}`);
    console.log(`📊 Formatos encontrados:`);
    console.log(`  - .jpg: ${imageFormats.jpg}`);
    console.log(`  - .jpeg: ${imageFormats.jpeg}`);
    console.log(`  - .png: ${imageFormats.png}`);
    console.log(`  - .avif: ${imageFormats.avif}`);
    console.log(`  - .webp: ${imageFormats.webp}`);
    console.log(`  - Otros: ${imageFormats.other}`);
    
    // Verificar si hay URLs problemáticas
    const problematicUrls = properties
      .filter(p => p.images)
      .flatMap(p => p.images)
      .filter(url => url.includes('.jpg') && !url.includes('.avif'));
    
    if (problematicUrls.length > 0) {
      console.log(`\n⚠️  URLs potencialmente problemáticas (.jpg sin .avif): ${problematicUrls.length}`);
      console.log('Ejemplos:');
      problematicUrls.slice(0, 3).forEach(url => {
        console.log(`  - ${url}`);
      });
    }
    
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

// Ejecutar el script
checkImageFormats();
