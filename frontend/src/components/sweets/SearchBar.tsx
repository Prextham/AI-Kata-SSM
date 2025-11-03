import React, { useState } from 'react';
import type { SearchParams } from '../../types';

interface SearchBarProps {
  onSearch: (params: SearchParams) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [searchParams, setSearchParams] = useState<SearchParams>({});
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSearch = () => {
    onSearch(searchParams);
  };

  const handleClear = () => {
    setSearchParams({});
    onSearch({});
  };

  return (
    <div className="card search-bar">
      <div className="search-controls">
        <input
          type="text"
          placeholder="Search by name..."
          value={searchParams.name || ''}
          onChange={(e) => setSearchParams({ ...searchParams, name: e.target.value })}
          className="input search-input"
        />
        <button onClick={handleSearch} className="btn btn-primary">
          Search
        </button>
        <button onClick={handleClear} className="btn btn-secondary">
          Clear
        </button>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="btn btn-secondary"
        >
          {showAdvanced ? 'Hide' : 'Advanced'}
        </button>
      </div>

      {showAdvanced && (
        <div className="search-advanced">
          <div className="form-group">
            <label>Category</label>
            <input
              type="text"
              placeholder="e.g., Chocolate"
              value={searchParams.category || ''}
              onChange={(e) => setSearchParams({ ...searchParams, category: e.target.value })}
              className="input"
            />
          </div>

          <div className="form-group">
            <label>Min Price (₹)</label>  {}
            <input
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={searchParams.min_price || ''}
                onChange={(e) => setSearchParams({ ...searchParams, min_price: parseFloat(e.target.value) || undefined })}
                className="input"
            />
            </div>

            <div className="form-group">
            <label>Max Price (₹)</label>  {}
            <input
                type="number"
                step="0.01"
                min="0"
                placeholder="1000.00"
                value={searchParams.max_price || ''}
                onChange={(e) => setSearchParams({ ...searchParams, max_price: parseFloat(e.target.value) || undefined })}
                className="input"
            />
            </div>
        </div>
      )}
    </div>
  );
};

export default SearchBar;
