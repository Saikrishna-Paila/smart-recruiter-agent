import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import JobList from './pages/JobList';
import JobDetail from './pages/JobDetail';
import JobCreate from './pages/JobCreate';
import CandidateDetail from './pages/CandidateDetail';
import ApplyForm from './pages/ApplyForm';
import './index.css';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/apply/:jobId" element={<ApplyForm />} />

          {/* Recruiter dashboard routes */}
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="jobs" element={<JobList />} />
            <Route path="jobs/new" element={<JobCreate />} />
            <Route path="jobs/:jobId" element={<JobDetail />} />
            <Route path="candidates/:candidateId" element={<CandidateDetail />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
