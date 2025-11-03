import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { sweetsAPI } from '../services/api';
import type { Sweet, SweetFormData, SearchParams } from '../types';
import { isAuthenticated, isAdmin as checkIsAdmin } from '../utils/auth';
import Navbar from '../components/layout/Navbar';
import SweetCard from '../components/sweets/SweetCard';
import SweetFormModal from '../components/sweets/SweetFormModal';
import SearchBar from '../components/sweets/SearchBar';

const Dashboard: React.FC = () => {
  const [sweets, setSweets] = useState<Sweet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingSweet, setEditingSweet] = useState<Sweet | undefined>();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
      return;
    }
    setIsAdmin(checkIsAdmin());
    fetchSweets();
  }, [navigate]);

  const fetchSweets = async () => {
    try {
      setLoading(true);
      const data = await sweetsAPI.getAll();
      setSweets(data);
      setError('');
    } catch (err: any) {
      setError('Failed to load sweets');
      if (err.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (params: SearchParams) => {
    try {
      setLoading(true);
      const data = Object.keys(params).length > 0 
        ? await sweetsAPI.search(params)
        : await sweetsAPI.getAll();
      setSweets(data);
      setError('');
    } catch (err) {
      setError('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (id: number, quantity: number) => {
    try {
      await sweetsAPI.purchase(id, quantity);
      fetchSweets();
      alert('Purchase successful!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Purchase failed');
    }
  };

  const handleAddEdit = async (data: SweetFormData) => {
    try {
      if (editingSweet) {
        await sweetsAPI.update(editingSweet.id, data);
      } else {
        await sweetsAPI.create(data);
      }
      setShowModal(false);
      setEditingSweet(undefined);
      fetchSweets();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Operation failed');
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this sweet?')) return;
    
    try {
      await sweetsAPI.delete(id);
      fetchSweets();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Delete failed');
    }
  };

  const openEditModal = (sweet: Sweet) => {
    setEditingSweet(sweet);
    setShowModal(true);
  };

  const openAddModal = () => {
    setEditingSweet(undefined);
    setShowModal(true);
  };

  if (loading && sweets.length === 0) {
    return (
      <div className="dashboard">
        <Navbar isAdmin={isAdmin} />
        <div className="container">
          <div className="loading-container">
            <div className="loading-icon">🍬</div>
            <p className="loading-text">Loading sweets...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <Navbar isAdmin={isAdmin} />
      
      <div className="container">
        <div className="dashboard-header">
          <h1 className="dashboard-title">Sweet Shop Dashboard</h1>
          {isAdmin && (
            <button onClick={openAddModal} className="btn btn-primary">
              + Add New Sweet
            </button>
          )}
        </div>

        <SearchBar onSearch={handleSearch} />

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {sweets.length === 0 ? (
          <div className="empty-container">
            <div className="empty-icon">🍬</div>
            <p className="empty-text">No sweets available</p>
            {isAdmin && (
              <button onClick={openAddModal} className="btn btn-primary mt-2">
                Add Your First Sweet
              </button>
            )}
          </div>
        ) : (
          <div className="sweet-grid">
            {sweets.map((sweet) => (
              <SweetCard
                key={sweet.id}
                sweet={sweet}
                isAdmin={isAdmin}
                onPurchase={handlePurchase}
                onEdit={openEditModal}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </div>

      {showModal && (
        <SweetFormModal
          sweet={editingSweet}
          onClose={() => {
            setShowModal(false);
            setEditingSweet(undefined);
          }}
          onSubmit={handleAddEdit}
        />
      )}
    </div>
  );
};

export default Dashboard;