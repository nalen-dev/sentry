import { jsPDF } from 'jspdf';
import { toPng } from 'html-to-image';
import { save } from '@tauri-apps/plugin-dialog';
import { writeFile } from '@tauri-apps/plugin-fs';
import { isTauri } from '@tauri-apps/api/core';

export const exportElementToPDF = async (elementId: string, filename: string) => {
  const element = document.getElementById(elementId);
  if (!element) {
    console.error(`Element with id ${elementId} not found.`);
    return;
  }

  // Optional: add a class to body to show loading state if needed
  try {
    // html-to-image is vastly faster and handles complex SVGs (Recharts) perfectly via foreignObject
    const imgData = await toPng(element, { 
      backgroundColor: '#0d1117',
      pixelRatio: 2,
      cacheBust: true,
      skipFonts: false
    });
    
    // Calculate dimensions
    const img = new Image();
    img.src = imgData;
    await new Promise((resolve) => { img.onload = resolve; });
    
    const pdf = new jsPDF('l', 'mm', 'a4');
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (img.height * pdfWidth) / img.width;
    
    // Create header text
    pdf.setFontSize(14);
    pdf.setTextColor(180); 
    pdf.text(`Exported Feature: ${filename}`, 14, 15);
    pdf.setFontSize(10);
    pdf.text(`Date: ${new Date().toLocaleString()}`, 14, 22);

    // Adjust image positioning to fit below header
    pdf.addImage(imgData, 'PNG', 10, 30, pdfWidth - 20, (pdfHeight * (pdfWidth - 20)) / pdfWidth);
    
    if (isTauri()) {
      // In Tauri desktop environment
      const filePath = await save({
        filters: [{ name: 'PDF Document', extensions: ['pdf'] }],
        defaultPath: `${filename}.pdf`
      });

      if (filePath) {
        const pdfBytes = pdf.output('arraybuffer');
        await writeFile(filePath, new Uint8Array(pdfBytes));
      }
    } else {
      // In browser fallback
      pdf.save(`${filename}.pdf`);
    }
  } catch (error) {
    console.error('Error generating PDF:', error);
  }
};
