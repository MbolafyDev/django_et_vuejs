// src/utils/format.ts
export function formatMoney(n: number) {
  return (n || 0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}
