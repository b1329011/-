import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import Profile from './pages/Profile';
import SetupProfile from './pages/SetupProfile';
import PartyDetail from './pages/PartyDetail';
import Admin from './pages/Admin';
import './App.css';

function App() {
  return (
    <Router basename="/nojo">
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/setup-profile" element={<SetupProfile />} />
        <Route path="/home" element={<Home />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/party/:id" element={<PartyDetail />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </Router>
  );
}

export default App;
