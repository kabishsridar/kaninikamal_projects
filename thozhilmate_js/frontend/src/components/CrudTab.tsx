import { Box, Button, Typography } from '@mui/material'
import { DataGrid, type GridRowsProp } from '@mui/x-data-grid'
import type { GridColDef } from '@mui/x-data-grid'
import { useCrud } from '../api/useCrud'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import IconButton from '@mui/material/IconButton'

type Meta = { columns: string[], pk: string[] }

function makeColumns(meta: Meta, onDelete?: (row:any)=>void): GridColDef[] {
  const pkSet = new Set(meta.pk)
  const cols = meta.columns.map((c) => ({
    field: c,
    headerName: c,
    flex: 1,
    editable: !pkSet.has(c)
  }))
  cols.push({
    field: '__actions',
    headerName: '',
    sortable: false,
    filterable: false,
    width: 70,
    renderCell: (params) => (
      <IconButton size="small" onClick={() => onDelete?.(params.row)}>
        <DeleteOutlineIcon />
      </IconButton>
    )
  })
  return cols
}


function getRowId(meta: Meta, row: any): string {
  if (meta.pk.length === 1) return row[meta.pk[0]]
  // composite key (order_items): synth id
  return meta.pk.map(k => row[k]).join(':')
}

export default function CrudTab({ table, meta }: { table: string, meta: Meta }) {
  const { list, refresh, createDefault, update, del, updateOrderItem, deleteOrderItem } = useCrud(table)
  const rows: GridRowsProp = (list.data ?? []).map(r => ({ id: getRowId(meta, r), ...r }))

  const onProcessRowUpdate = async (newRow: any, oldRow: any) => {
    // diff -> send only changed fields (optional)
    const body: any = { ...newRow }
    meta.pk.forEach(k => delete body[k]) // do not send PKs

    if (table === 'order_items') {
      const [order_id, line_no] = newRow.id.split(':')
      await updateOrderItem.mutateAsync({ order_id, line_no: Number(line_no), body })
    } else {
      await update.mutateAsync({ id: newRow[meta.pk[0]], body })
    }
    return newRow
  }

  const handleDelete = async (row: any) => {
    if (table === 'order_items') {
      const [order_id, line_no] = row.id.split(':')
      await deleteOrderItem.mutateAsync({ order_id, line_no: Number(line_no) })
    } else {
      await del.mutateAsync(row[meta.pk[0]])
    }
  }

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
        <Button variant="contained" onClick={() => createDefault.mutate()} disableElevation>Insert Row</Button>
        <Button variant="outlined" onClick={() => refresh()}>Refresh</Button>
        <Typography variant="body2" sx={{ ml: 'auto', opacity: .7 }}>
          Double-click a cell to edit • Press Enter to save
        </Typography>
      </Box>
      <DataGrid
        autoHeight
        rows={rows}
        columns={makeColumns(meta, handleDelete)}
        experimentalFeatures={{ newEditingApi: true }}
        processRowUpdate={onProcessRowUpdate}
        onProcessRowUpdateError={(e) => console.error(e)}
        pageSizeOptions={[5, 10, 25, 100]}
        initialState={{ pagination: { paginationModel: { pageSize: 10, page: 0 }}}}
        disableRowSelectionOnClick
        slots={{
          noRowsOverlay: () => <Typography sx={{ p: 2 }}>No data — click “Insert Row”.</Typography>,
        }}
        onRowDoubleClick={async (p) => {}}
        onRowClick={() => {}}
        slotProps={{
          row: {
            onContextMenu: (e: any) => e.preventDefault()
          }
        }}
        getRowId={(r) => r.id}
        onRowSelectionModelChange={async () => {}}
        checkboxSelection
        sx={{
          '& .MuiDataGrid-cell': { outline: 'none' }
        }}
      />
      <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
        <Button
          color="error"
          variant="contained"
          onClick={async () => {
            const sel = (document.querySelector('[data-rowselection="true"]') as any)
            // Simpler: delete first selected row via DOM is tricky; instead rely on DataGrid API in parent integrations.
            alert('Select a row using the left checkbox, then click the row’s overflow menu to delete in your own extension.\nFor now, use the row menu in your presentation or add a Delete icon column.\nAlternatively, click a row and press DEL if you wire key handlers.')
          }}
          disabled
        >
          Delete (wire selection)
        </Button>
      </Box>
      {/* Simpler approach: add per-row delete icon column if you prefer. See note below. */}
    </Box>
  )
}
