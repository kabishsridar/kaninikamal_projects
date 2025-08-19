import { useQuery } from '@tanstack/react-query'
import { api } from './client'

export function useMeta() {
  return useQuery({
    queryKey: ['meta'],
    queryFn: async () => (await api.get('/meta')).data as Record<string, { columns: string[], pk: string[] }>
  })
}
