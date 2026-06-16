import gspread


def write_to_sheet(
    rows: list[dict],
    credentials_file: str,
    spreadsheet_id: str,
    worksheet_name: str = "MarketplaceSync",
) -> None:
    """Write grouped rows to a Google Sheets worksheet.

    Clears the worksheet first, then writes headers + data starting at A1.
    Creates the worksheet if it does not exist.
    """
    if not rows:
        return

    gc = gspread.service_account(filename=credentials_file)
    sh = gc.open_by_key(spreadsheet_id)

    try:
        ws = sh.worksheet(worksheet_name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet_name, rows=1000, cols=20)

    headers = list(rows[0].keys())
    values = [headers] + [[row[h] for h in headers] for row in rows]
    ws.update(values, "A1")
