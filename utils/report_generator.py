"""
PDF Report Generator using ReportLab (supports Unicode, with fixed column widths)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime
import pandas as pd

def generate_report(results_df_display: pd.DataFrame, jd_preview: str, matcher_name: str, output_path: str = "screening_report.pdf") -> str:
    """
    Generate a PDF report with fixed column widths to prevent overflow.
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4, 
                            leftMargin=0.5*inch, rightMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch,
                            title="Resume Screening Report")
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='Normal_Unicode', parent=styles['Normal'], fontName='Helvetica', fontSize=9))
    styles.add(ParagraphStyle(name='Title_Unicode', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=14))
    styles.add(ParagraphStyle(name='Heading_Unicode', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11))
    styles.add(ParagraphStyle(name='TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, alignment=1))
    styles.add(ParagraphStyle(name='TableCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=0))
    
    story = []
    
    # Title
    story.append(Paragraph("Resume Screening Report", styles['Title_Unicode']))
    story.append(Spacer(1, 12))
    
    # Metadata
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal_Unicode']))
    story.append(Paragraph(f"Matcher: {matcher_name}", styles['Normal_Unicode']))
    story.append(Spacer(1, 12))
    
    # JD preview
    story.append(Paragraph("Job Description (excerpt):", styles['Heading_Unicode']))
    jd_para = Paragraph(jd_preview, styles['Normal_Unicode'])
    story.append(jd_para)
    story.append(Spacer(1, 12))
    
    # Table header
    top_results = results_df_display.head(20)
    actual_count = len(top_results)
    story.append(Paragraph(f"Ranked Candidates ({actual_count} candidate{'s' if actual_count != 1 else ''}):", styles['Heading_Unicode']))
    story.append(Spacer(1, 6))
    
    # Define column widths
    col_widths = [0.5*inch, 1.5*inch, 0.7*inch, 0.5*inch, 1.2*inch, 2.4*inch]
    
    # Header
    headers = ["Rank", "Filename", "Match %", "Exp (yrs)", "Degrees", "Key Skills"]
    table_data = [[Paragraph(h, styles['TableHeader']) for h in headers]]
    
    for _, row in top_results.iterrows():
        rank = str(row['Rank'])
        filename = str(row['Filename'])[:30]
        # Match score
        if 'Match_Score' in row:
            match_score = f"{row['Match_Score']:.1f}%"
        elif 'Hybrid_Score' in row:
            match_score = f"{row['Hybrid_Score']:.1f}%"
        else:
            match_score = "N/A"
        exp = str(row.get('Experience (yrs)', 'N/A'))
        degrees = str(row.get('Degrees', 'N/A'))[:25]
        skills = str(row.get('Detected_Skills', 'N/A'))[:50]
        if len(skills) > 50:
            skills = skills[:47] + "..."
        
        row_data = [
            Paragraph(rank, styles['TableCell']),
            Paragraph(filename, styles['TableCell']),
            Paragraph(match_score, styles['TableCell']),
            Paragraph(exp, styles['TableCell']),
            Paragraph(degrees, styles['TableCell']),
            Paragraph(skills, styles['TableCell'])
        ]
        table_data.append(row_data)
    
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Note: Full results (CSV) contain all candidates and detailed scores.", styles['Normal_Unicode']))
    
    doc.build(story)
    return output_path