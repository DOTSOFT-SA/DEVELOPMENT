import { BrowserRouter, Route, Routes } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import NotFound from "./components/NotFound.jsx";
import ProtectedRoute from "./auth/ProtectedRoute";
import Home from "./pages/Home.jsx";
import DemandForecasting from "./pages/DemandForecasting.jsx";
import DemandForecastingInputData from "./pages/DemandForecastingInputData.jsx";
import InventoryOptimization from "./pages/InventoryOptimization.jsx";
import DistributionOptimization from "./pages/DistributionOptimization.jsx";
import DistributionOptimizationInputData from "./pages/DistributionOptimizationInputData.jsx";
import ManageUsers from "./pages/ManageUsers.jsx";
import TermsOfUse from "./pages/TermsOfUse.jsx";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Public Login Route */}
                <Route path="/" element={<Login />} />

                {/* Protected Dashboard Route */}
                <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>}>
                    <Route path="/dashboard/home" element={<Home />} />
                    <Route path="/dashboard/demand-forecasting" element={<DemandForecasting />} />
                    <Route path="/dashboard/demand-forecasting-input-data" element={<ProtectedRoute><DemandForecastingInputData /></ProtectedRoute>} />
                    <Route path="/dashboard/inventory-optimization" element={<InventoryOptimization />} />
                    <Route path="/dashboard/distribution-optimization" element={<DistributionOptimization />} />
                    <Route path="/dashboard/distribution-optimization-input-data" element={<DistributionOptimizationInputData/>} />
                    <Route path="/dashboard/manage-users" element={<ManageUsers/>} />
                </Route>

                <Route path="/terms-of-use" element={<TermsOfUse/>} />

                {/* Catch-All for Not Found */}
                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
