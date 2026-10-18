import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ForgotPassword from "./pages/ForgotPassword";
import Dashboard from "./pages/Dashboard";
import Results from "./pages/Results";
import Create from "./pages/Create";
import Publish from "./pages/Publish";
import ProtectedRoute from "./components/ProtectedRoute";

// Importações das novas páginas:
import Channels from "./pages/Channels"; 
import Guide from "./pages/Guide"; // <-- IMPORTAÇÃO DO GUIA ADICIONADA AQUI


function Router() {
  // make sure to consider if you need authentication for certain routes
  return (
    <Switch>
      <Route path="/" component={Landing} />
      <Route path="/login" component={Login} />
      <Route path="/signup" component={Signup} />
      <Route path="/forgot-password" component={ForgotPassword} />
      <Route path="/dashboard">{() => <ProtectedRoute component={Dashboard} />}</Route>
      <Route path="/results">{() => <ProtectedRoute component={Results} />}</Route>
      <Route path="/create">{() => <ProtectedRoute component={Create} />}</Route>
      <Route path="/publish">{() => <ProtectedRoute component={Publish} />}</Route>
      
      {/* Rotas Adicionadas: */}
      <Route path="/channels">{() => <ProtectedRoute component={Channels} />}</Route>
      <Route path="/guide">{() => <ProtectedRoute component={Guide} />}</Route> {/* <-- NOVA ROTA DO GUIA ADICIONADA AQUI */}
      
      <Route path="/404" component={NotFound} />
      {/* Final fallback route */}
      <Route component={NotFound} />
    </Switch>
  );
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;