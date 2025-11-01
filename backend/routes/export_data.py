"""Export API endpoints for CSV, JSON, and PDF."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from routes.sessions import sessions_db
from routes.tags import tags_db
import csv
import io
import json
from datetime import datetime

router = APIRouter()


@router.get("/csv/{session_id}")
async def export_csv(session_id: str):
    """Export session as CSV."""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    session = sessions_db[session_id]

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "Trace ID",
        "User Input",
        "Agent Output",
        "System Prompt",
        "Pass/Fail",
        "Open Code",
        "Axial Tags",
        "Reviewer ID",
        "Reviewed At",
        "Metadata"
    ])

    # Write trace data
    for trace in session.traces:
        # Get tag names
        tag_names = [
            tags_db[tag_id].name
            for tag_id in trace.axial_tags
            if tag_id in tags_db
        ]

        writer.writerow([
            trace.id,
            trace.user_input,
            trace.agent_output,
            trace.system_prompt or "",
            trace.pass_fail or "",
            trace.open_code or "",
            ", ".join(tag_names),
            trace.reviewer_id or "",
            trace.reviewed_at.isoformat() if trace.reviewed_at else "",
            json.dumps(trace.metadata)
        ])

    # Prepare response
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=session_{session_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/json/{session_id}")
async def export_json(session_id: str):
    """Export session as JSON."""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    session = sessions_db[session_id]

    # Convert to dict for JSON serialization
    session_dict = session.model_dump(mode='json')

    # Prepare response
    return JSONResponse(
        content=session_dict,
        headers={
            "Content-Disposition": f"attachment; filename=session_{session_id}_{datetime.now().strftime('%Y%m%d')}.json"
        }
    )


@router.get("/pdf/{session_id}")
async def export_pdf(session_id: str):
    """Generate PDF report."""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    session = sessions_db[session_id]

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors

        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#3B82F6')
        )
        story.append(Paragraph(f"EvalSwipe Report: {session.name or session.id}", title_style))
        story.append(Spacer(1, 0.3*inch))

        # Summary statistics
        story.append(Paragraph("Summary Statistics", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))

        summary_data = [
            ["Total Traces", str(session.total_traces)],
            ["Reviewed", str(session.reviewed_count)],
            ["Passed", str(session.passed_count)],
            ["Failed", str(session.failed_count)],
            ["Deferred", str(session.deferred_count)],
            ["Pass Rate", f"{(session.passed_count / max(session.reviewed_count, 1) * 100):.1f}%"]
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))

        # Failure mode distribution
        if session.axial_tags:
            story.append(Paragraph("Failure Mode Distribution", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))

            failure_data = [["Tag", "Count"]]
            for tag in session.axial_tags:
                if tag.usage_count > 0:
                    failure_data.append([tag.name, str(tag.usage_count)])

            if len(failure_data) > 1:
                failure_table = Table(failure_data, colWidths=[3*inch, 1*inch])
                failure_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                ]))
                story.append(failure_table)
            else:
                story.append(Paragraph("No failure modes recorded", styles['Normal']))

        # Build PDF
        doc.build(story)

        # Prepare response
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=session_{session_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )

    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF generation requires reportlab library"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}"
        )
