import React, { useState } from 'react';
import type { Sweet } from '../../types';

interface SweetCardProps {
  sweet: Sweet;
  isAdmin: boolean;
  onPurchase: (id: number, quantity: number) => void;
  onEdit: (sweet: Sweet) => void;
  onDelete: (id: number) => void;
}

const SweetCard: React.FC<SweetCardProps> = ({ sweet, isAdmin, onPurchase, onEdit, onDelete }) => {
  const [purchaseQuantity, setPurchaseQuantity] = useState(1);
  const [showPurchaseInput, setShowPurchaseInput] = useState(false);

  const handlePurchase = () => {
    if (purchaseQuantity > 0 && purchaseQuantity <= sweet.quantity) {
      onPurchase(sweet.id, purchaseQuantity);
      setPurchaseQuantity(1);
      setShowPurchaseInput(false);
    }
  };

  return (
    <div className="sweet-card">
      <div className="sweet-card-header">
        <div>
          <h3 className="sweet-card-title">{sweet.name}</h3>
          <p className="sweet-card-category">{sweet.category}</p>
        </div>
        <div>
            <p className="sweet-card-price">₹{sweet.price.toFixed(2)}</p>
        </div>
      </div>

      <div className="sweet-card-stock">
        <span className="stock-label">Stock:</span>
        <span className={`stock-value ${sweet.quantity === 0 ? 'stock-out' : 'stock-available'}`}>
          {sweet.quantity} {sweet.quantity === 0 ? '(Out of stock)' : 'available'}
        </span>
      </div>

      <div className="sweet-card-actions">
        {!showPurchaseInput ? (
          <button
            onClick={() => setShowPurchaseInput(true)}
            disabled={sweet.quantity === 0}
            className="btn btn-primary btn-full"
          >
            {sweet.quantity === 0 ? 'Out of Stock' : 'Purchase'}
          </button>
        ) : (
          <div className="purchase-form">
            <input
              type="number"
              min="1"
              max={sweet.quantity}
              value={purchaseQuantity}
              onChange={(e) => setPurchaseQuantity(parseInt(e.target.value) || 1)}
              className="input purchase-input"
              placeholder="Quantity"
            />
            <button onClick={handlePurchase} className="btn btn-primary">
              Buy
            </button>
            <button onClick={() => setShowPurchaseInput(false)} className="btn btn-secondary">
              Cancel
            </button>
          </div>
        )}

        {isAdmin && (
          <div className="admin-actions">
            <button
              onClick={() => onEdit(sweet)}
              className="btn btn-secondary btn-small"
            >
              Edit
            </button>
            <button
              onClick={() => onDelete(sweet.id)}
              className="btn btn-danger btn-small"
            >
              Delete
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SweetCard;
