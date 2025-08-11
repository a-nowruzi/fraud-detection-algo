import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import PredictPage from './pages/PredictPage';
import ChartsPage from './pages/ChartsPage';
import StatsPage from './pages/StatsPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/predict" element={<PredictPage />} />
          <Route path="/charts" element={<ChartsPage />} />
          <Route path="/stats" element={<StatsPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
