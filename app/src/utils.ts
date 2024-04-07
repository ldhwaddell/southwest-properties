export const formatSnakeCaseToTitle = (text: string): string => {
    const words = text.split("_");
  
    // Capitalize the first letter of each word and join them with a space
    const formattedText = words
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  
    return formattedText;
  };