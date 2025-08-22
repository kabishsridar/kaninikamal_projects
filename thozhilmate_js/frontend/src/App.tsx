import * as React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Box, Container, Tab, Tabs, Toolbar, AppBar, Typography, CircularProgress } from '@mui/material'
import CrudTab from './components/CrudTab'
import { useMeta } from './api/useMeta'

const qc = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <Main />
    </QueryClientProvider>
  )
}

function Main() {
  const { data: meta, isLoading, error } = useMeta()
  const [tab, setTab] = React.useState(0)
  const tables = meta ? Object.keys(meta) : []

  return (
    <Box>
      {/* Top App Bar */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Thozhilmate Automation with React
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main Container */}
      <Container maxWidth="xl" sx={{ mt: 3 }}>
        {/* Loading & Error States */}
        {isLoading && (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
          </Box>
        )}
        {error && <Typography color="error">Failed to load metadata.</Typography>}

        {/* Tabs and Content */}
        {!isLoading && meta && (
          <>
            <Tabs
              value={tab}
              onChange={(_, v) => setTab(v)}
              sx={{ mb: 2 }}
              variant="scrollable"
              scrollButtons="auto"
            >
              {tables.map((t) => (
                <Tab key={t} label={t.replace(/_/g, ' ').toUpperCase()} />
              ))}
            </Tabs>

            <Box>
              {/* Render only active tab */}
              {tables.length > 0 && (
                <CrudTab table={tables[tab]} meta={meta[tables[tab]]} />
              )}
            </Box>
          </>
        )}
      </Container>
    </Box>
  )
}
