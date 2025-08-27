import jsPDF from 'jspdf';
import 'jspdf-autotable';

// Extend jsPDF with the autoTable plugin
interface jsPDFWithAutoTable extends jsPDF {
  autoTable: (options: any) => jsPDF;
}

export const generatePdf = (results: any) => {
  const doc = new jsPDF() as jsPDFWithAutoTable;
  const { panels, materials_summary, compliance, crate_dimensions, cost_estimate } = results;

  // 1. Header
  doc.setFontSize(20);
  doc.text('AutoCrate V12 - Crate Design Report', 14, 22);
  doc.setFontSize(12);
  doc.text(`Report Generated: ${new Date().toLocaleString()}`, 14, 30);

  // 2. Crate Summary
  doc.setFontSize(16);
  doc.text('Crate Summary', 14, 45);
  doc.autoTable({
    startY: 50,
    head: [['Metric', 'Value']],
    body: [
      ['External Dimensions (LxWxH)', `${crate_dimensions.length.toFixed(2)}" x ${crate_dimensions.width.toFixed(2)}" x ${crate_dimensions.height.toFixed(2)}"`],
      ['Estimated Weight', `${cost_estimate.weight.toFixed(2)} lbs`],
      ['Estimated Cost', `$${cost_estimate.total.toFixed(2)}`],
      ['Estimated Lead Time', `${cost_estimate.leadTime} days`],
      ['Compliance Status', compliance.status],
    ],
    theme: 'striped',
    headStyles: { fillColor: [22, 160, 133] },
  });

  // 3. Bill of Materials (Panels)
  let finalY = (doc as any).lastAutoTable.finalY || 80;
  doc.setFontSize(16);
  doc.text('Bill of Materials - Panels', 14, finalY + 15);
  doc.autoTable({
    startY: finalY + 20,
    head: [['Panel Type', 'Dimensions (in)', 'Material', 'Qty', 'Status']],
    body: Object.entries(panels).map(([key, panel]: [string, any]) => [
      key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      `${panel.length.toFixed(2)} x ${panel.width.toFixed(2)} x ${panel.thickness.toFixed(2)}`,
      panel.material,
      panel.quantity,
      panel.status === 'Calculated' ? 'OK' : 'Error'
    ]),
    theme: 'grid',
    headStyles: { fillColor: [41, 128, 185] },
  });

  // 4. Materials Summary
  finalY = (doc as any).lastAutoTable.finalY;
  doc.setFontSize(16);
  doc.text('Materials Summary', 14, finalY + 15);
  doc.autoTable({
    startY: finalY + 20,
    head: [['Material', 'Details']],
    body: [
      ['Plywood Sheets', `Count: ${materials_summary.plywood_sheets_4x8.count}, Type: ${materials_summary.plywood_sheets_4x8.type}`],
      ['Lumber (Cleats)', `Total Length: ${materials_summary.cleat_summary.total_length_ft.toFixed(2)} ft, Type: ${materials_summary.cleat_summary.type}`],
    ],
    theme: 'striped',
    headStyles: { fillColor: [22, 160, 133] },
  });

  // 5. Footer
  const pageCount = (doc.internal as any).getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(10);
    doc.text(`Page ${i} of ${pageCount}`, doc.internal.pageSize.width - 30, doc.internal.pageSize.height - 10);
    doc.text('AutoCrate V12 © 2024 - Confidential & Proprietary', 14, doc.internal.pageSize.height - 10);
  }

  // Save the PDF
  const now = new Date();
  const filename = `${now.getFullYear()}${(now.getMonth()+1).toString().padStart(2,'0')}${now.getDate().toString().padStart(2,'0')}_${now.getHours().toString().padStart(2,'0')}${now.getMinutes().toString().padStart(2,'0')}${now.getSeconds().toString().padStart(2,'0')}_Crate_Report.pdf`;
  doc.save(filename);
};
