import NavBar from "./components/NavBar";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Main from "./components/Main";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="d-flex flex-column site-container mx-2">
        <NavBar />
        <Main />
      </div>
    </QueryClientProvider>
  );
}

export default App;
