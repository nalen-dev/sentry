import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';

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
    pdf.setTextColor(40);
    pdf.text(`Exported Feature: ${filename}`, 14, 15);
    pdf.setFontSize(10);
    pdf.text(`Date: ${new Date().toLocaleString()}`, 14, 22);

    // Adjust image positioning to fit below header
    pdf.addImage(imgData, 'PNG', 10, 30, pdfWidth - 20, (pdfHeight * (pdfWidth - 20)) / pdfWidth);
    pdf.save(`${filename}.pdf`);
  } catch (error) {
    console.error('Error generating PDF:', error);
  }
};
