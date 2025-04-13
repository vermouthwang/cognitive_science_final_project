export const processBase64Image = (dataUrl: string): string => {
  try {
    // If it's already a base64 string without data URL prefix, return it
    if (!dataUrl.includes('data:image')) {
      return dataUrl;
    }
    
    // Extract the base64 part from the data URL
    const base64String = dataUrl.split(',')[1];
    
    // Clean the base64 string
    const cleaned = base64String.replace(/[^A-Za-z0-9+/]/g, '');
    
    // Add padding if necessary
    const pad = cleaned.length % 4;
    const padded = pad ? cleaned + '='.repeat(4 - pad) : cleaned;
    
    return padded;
  } catch (error) {
    console.error('Error processing base64 image:', error);
    throw error;
  }
}; 