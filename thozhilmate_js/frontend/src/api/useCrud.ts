import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from './client'

export function useCrud(table: string) {
  const qc = useQueryClient()
  const list = useQuery({
    queryKey: [table, 'list'],
    queryFn: async () => (await api.get(`/${table}`)).data as any[]
  })

  const refresh = () => qc.invalidateQueries({ queryKey: [table, 'list'] })

  const createDefault = useMutation({
    mutationFn: async () => (await api.post(`/${table}/create_default`)).data,
    onSuccess: () => refresh()
  })

  const update = useMutation({
    mutationFn: async (payload: { id: string, body: any }) => {
      return (await api.put(`/${table}/${payload.id}`, payload.body)).data
    },
    onSuccess: () => refresh()
  })

  const del = useMutation({
    mutationFn: async (id: string) => (await api.delete(`/${table}/${id}`)).data,
    onSuccess: () => refresh()
  })

  // Special for order_items (composite key)
  const updateOrderItem = useMutation({
    mutationFn: async (p: { order_id: string, line_no: number, body: any }) =>
      (await api.put(`/order_items/${p.order_id}/${p.line_no}`, p.body)).data,
    onSuccess: () => refresh()
  })
  const deleteOrderItem = useMutation({
    mutationFn: async (p: { order_id: string, line_no: number }) =>
      (await api.delete(`/order_items/${p.order_id}/${p.line_no}`)).data,
    onSuccess: () => refresh()
  })

  return { list, refresh, createDefault, update, del, updateOrderItem, deleteOrderItem }
}
