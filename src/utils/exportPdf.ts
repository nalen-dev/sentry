import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import { save } from '@tauri-apps/plugin-dialog';
import { writeFile } from '@tauri-apps/plugin-fs';

export const exportElementToPDF = async (elementId: string, filename: string) => {
  const element = document.getElementById(elementId);
  if (!element) {
    console.error(`Element with id ${elementId} not found.`);
    return;
  }

  try {
    const canvas = await html2canvas(element, { scale: 2, useCORS: true, backgroundColor: '#0d1117' });
    const imgData = canvas.toDataURL('image/png');
    
    const pdf = new jsPDF('l', 'mm', 'a4');
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
    
    // Create header text
    pdf.setFontSize(14);
    pdf.setTextColor(180); // Lighter text for dark theme PDF or keep it visible
    pdf.text(`Exported Feature: ${filename}`, 14, 15);
    pdf.setFontSize(10);
    pdf.text(`Date: ${new Date().toLocaleString()}`, 14, 22);

    // Adjust image positioning to fit below header
    pdf.addImage(imgData, 'PNG', 10, 30, pdfWidth - 20, (pdfHeight * (pdfWidth - 20)) / pdfWidth);
    
    if ('__TAURI_INTERNALS__' in window) {
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
