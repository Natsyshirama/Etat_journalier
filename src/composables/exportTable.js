import * as XLSX from 'xlsx'

export function exportTable({
  rows = [],
  columns = [],
  filename = 'export',
  format = 'xlsx',
  sheetName = 'Données'
}) {
  if (!rows.length) {
    window.alert('Aucune donnée à exporter')
    return
  }

  const data = rows.map((row) => {
    const result = {}

    columns.forEach(({ key, title }) => {
      result[title || key] = row[key] ?? ''
    })

    return result
  })

  const worksheet = XLSX.utils.json_to_sheet(data)
  const workbook = XLSX.utils.book_new()

  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)

  const extension = format === 'csv' ? 'csv' : 'xlsx'

  XLSX.writeFile(
    workbook,
    `${filename}_${new Date().toISOString().slice(0, 10)}.${extension}`,
    {
      bookType: extension,
      FS: ';'
    }
  )
}