import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./components/AppLayout";
import Login from "./pages/Login";
import Resumen from "./pages/Resumen";
import Mora from "./pages/Mora";
import Creditos from "./pages/Creditos";
import Clientes from "./pages/Clientes";
import Cuentas from "./pages/Cuentas";
import Desembolsos from "./pages/Desembolsos";
import Configuracion from "./pages/Configuracion";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route path="/" element={<Resumen />} />
                <Route path="/creditos" element={<Creditos />} />
                <Route path="/mora" element={<Mora />} />
                <Route path="/clientes" element={<Clientes />} />
                <Route path="/cuentas" element={<Cuentas />} />
                <Route path="/desembolsos" element={<Desembolsos />} />
                <Route path="/configuracion" element={<Configuracion />} />
              </Route>
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
