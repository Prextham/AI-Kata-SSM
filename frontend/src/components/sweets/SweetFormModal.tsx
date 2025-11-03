import React, { useState, useEffect } from 'react';
import type { Sweet, SweetFormData } from '../../types';

interface SweetFormModalProps {
  sweet?: Sweet;
  onClose: () => void;
  onSubmit: (data: SweetFormData) => void;
}

const SweetFormModal: React.FC<SweetFormModalProps> = ({ sweet, onClose, onSubmit }) => {
  const [formData, setFormData] = useState<SweetFormData>({
    name: '',
    category: '',
    price: 0,
    quantity: 0,
  });

  useEffect(() => {
    if (sweet) {
      setFormData({
        name: sweet.name,
        category: sweet.category,
        price: sweet.price,
        quantity: sweet.quantity,
      });
    }
  }, [sweet]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="modal-overlay">
      <div className="card modal-content">
        <h3 className="modal-title">
          {sweet ? 'Edit Sweet' : 'Add New Sweet'}
        </h3>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input"
              required
            />
          </div>

          <div className="form-group">
            <label>Category</label>
            <input
              type="text"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="input"
              required
            />
          </div>

          <div className="form-group">
            <label>Price (₹)</label>  {/* Changed */}
            <input
                type="number"
                step="0.01"
                min="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
                className="input"
                required
                placeholder="e.g., 50.00"
            />
            </div>

          <div className="form-group">
            <label>Quantity</label>
            <input
              type="number"
              min="0"
              value={formData.quantity}
              onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) })}
              className="input"
              required
            />
          </div>

          <div className="modal-actions">
            <button type="submit" className="btn btn-primary">
              {sweet ? 'Update' : 'Add'} Sweet
            </button>
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SweetFormModal;
