import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { removeToken, getUsername } from '../../utils/auth';

interface NavbarProps {
  isAdmin: boolean;
}

const Navbar: React.FC<NavbarProps> = ({ isAdmin }) => {
  const navigate = useNavigate();
  const username = getUsername();

  const handleLogout = () => {
    removeToken();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="container navbar-container">
        <Link to="/dashboard" className="navbar-brand">
          <span className="navbar-brand-icon">🍬</span>
          <span className="navbar-brand-text">Sweet Shop</span>
        </Link>

        <div className="navbar-user">
          <span className="navbar-username">
            Welcome, <strong>{username}</strong>
            {isAdmin && <span className="admin-badge">Admin</span>}
          </span>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
