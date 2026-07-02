import { useQuery } from "@tanstack/react-query";
import { api } from "./api";
import type { MiCuenta } from "./types";

export function useMiCuenta() {
  return useQuery({
    queryKey: ["mi-cuenta"],
    queryFn: async () => {
      const { data } = await api.get<MiCuenta>("/homebanking/mi-cuenta");
      return data;
    },
  });
}
