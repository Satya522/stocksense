import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { PackageSearch, RefreshCw, Search, ListFilter, ChevronDown, Download, Edit2, ShoppingCart, MoreVertical, Plus, X, Check, Eye, AlertCircle } from 'lucide-react';
import Papa from 'papaparse';
import * as XLSX from 'xlsx';
import { api } from '../lib/api';
import '../styles/inventory.css';

const STATUS_CLASS = {
  critical: 'critical',
  danger: 'critical',
  warning: 'warning',
  healthy: 'healthy',
  success: 'healthy',
};

function formatIndianNumber(value) {
  if (value === null || value === undefined || value === '') return '—';
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return String(value);
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(numeric);
}

function formatCurrency(value) {
  if (value === null || value === undefined || value === '') return '—';
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return String(value);
  const negative = numeric < 0;
  const formatted = formatIndianNumber(Math.abs(numeric));
  return `${negative ? '-' : ''}${formatted}`;
}

function normalizeStatus(status = '') {
  return String(status).trim().toLowerCase();
}

function StatusBadge({ status }) {
  const normalized = normalizeStatus(status);
  const tone = STATUS_CLASS[normalized] || 'warning';
  const label = status || '—';
  return <span className={`badge ${tone}`}>{label}</span>;
}

function LevelBar({ levelPercent, status }) {
  if (levelPercent === null || levelPercent === undefined) return null;
  const clamped = Math.max(0, Math.min(100, Number(levelPercent)));
  const tone = STATUS_CLASS[normalizeStatus(status)] || 'warning';
  return (
    <div className="level-track" aria-label={`Inventory level ${clamped}%`}>
      <span className={`level-fill ${tone}`} style={{ width: `${clamped}%` }} />
    </div>
  );
}

function SkeletonRows({ rows = 8 }) {
  return (
    <>
      {Array.from({ length: rows }).map((_, index) => (
        <tr className="skeleton-row" key={`skeleton-${index}`} aria-hidden="true">
          <td><span className="skeleton-line skeleton-item" /></td>
          <td><span className="skeleton-line skeleton-code" /></td>
          <td><span className="skeleton-line skeleton-warehouse" /></td>
          <td className="numeric"><span className="skeleton-line skeleton-num" /></td>
          <td className="numeric"><span className="skeleton-line skeleton-num short" /></td>
          <td className="numeric"><span className="skeleton-line skeleton-value" /></td>
          <td><span className="skeleton-line skeleton-level" /></td>
          <td><span className="skeleton-line skeleton-status" /></td>
        </tr>
      ))}
    </>
  );
}

function useClickOutside(ref, handler) {
  useEffect(() => {
    const listener = (event) => {
      if (!ref.current || ref.current.contains(event.target)) return;
      handler(event);
    };
    document.addEventListener("mousedown", listener);
    return () => document.removeEventListener("mousedown", listener);
  }, [ref, handler]);
}

// -------------------------------------------------------------
// CUSTOM PREMIUM SELECT DROPDOWN
// -------------------------------------------------------------
function CustomSelect({ options, value, onChange, placeholder }) {
  const [open, setOpen] = useState(false);
  const ref = useRef();
  useClickOutside(ref, () => setOpen(false));
  const selected = options.find(o => o.value === value);

  return (
    <div className="custom-select" ref={ref}>
      <div className={`custom-select-trigger ${open ? 'is-open' : ''}`} onClick={() => setOpen(!open)}>
        <span>{selected && selected.value !== '' ? selected.label : placeholder}</span>
        <ChevronDown size={14} className="select-icon" />
      </div>
      {open && (
        <div className="custom-select-menu">
          {options.map(opt => (
            <div 
              key={opt.value} 
              className={`custom-select-item ${value === opt.value ? 'selected' : ''}`} 
              onClick={() => { onChange(opt.value); setOpen(false); }}
            >
              {opt.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const NUMBER_OPS = [
  { value: '', label: 'None' },
  { value: '==', label: 'Equals' },
  { value: '!=', label: 'Does Not Equal' },
  { value: '>', label: 'Greater Than' },
  { value: '>=', label: 'Greater Than Or Equal' },
  { value: '<', label: 'Less Than' },
  { value: '<=', label: 'Less Than Or Equal' },
];

const TEXT_OPS = [
  { value: '', label: 'None' },
  { value: 'contains', label: 'Contains' },
  { value: 'not_contains', label: 'Does Not Contain' },
  { value: 'starts_with', label: 'Starts With' },
  { value: 'ends_with', label: 'Ends With' },
  { value: 'exact', label: 'Equals' },
];

// -------------------------------------------------------------
// EXCEL FILTER COMPONENT
// -------------------------------------------------------------
function ExcelFilter({ title, colKey, type, options, filterState, onChange, onSort, sortConfig, align = 'right' }) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  
  // Local state for Conditions to avoid closing popup on every keystroke
  const [condOp, setCondOp] = useState(filterState?.condOp || '');
  const [condVal, setCondVal] = useState(filterState?.condVal ?? '');

  const ref = useRef(null);
  useClickOutside(ref, () => setIsOpen(false));
  
  const handleSort = (dir) => {
    onSort({ key: colKey, direction: dir });
    setIsOpen(false);
  };

  const applyConditionFilter = () => {
    onChange(colKey, { ...filterState, condOp, condVal, type });
    setIsOpen(false);
  };
  
  const clearConditionFilter = () => {
    setCondOp('');
    setCondVal('');
    onChange(colKey, { ...filterState, condOp: '', condVal: '', type });
    setIsOpen(false);
  };

  const [draftIn, setDraftIn] = useState(filterState?.in || []);

  useEffect(() => {
    if (isOpen) {
      setDraftIn(filterState?.in || []);
    }
  }, [isOpen, filterState?.in]);

  const handleCheckbox = (opt, isChecked) => {
    if (isChecked) {
      setDraftIn([...draftIn, opt]);
    } else {
      setDraftIn(draftIn.filter(x => x !== opt));
    }
  };

  const filteredOptions = useMemo(() => {
    return options.filter(o => String(o.label).toLowerCase().includes(search.toLowerCase()));
  }, [options, search]);

  const displayOptions = filteredOptions.slice(0, 100);

  const selectAll = () => setDraftIn(filteredOptions.map(o => o.value));
  const clearAll = () => setDraftIn([]);

  const isActive = (filterState?.in && filterState.in.length > 0) || (filterState?.condOp && filterState?.condVal !== '');
  const isAllSelected = filteredOptions.length > 0 && draftIn.length === filteredOptions.length;

  const isSortedAsc = sortConfig?.key === colKey && sortConfig?.direction === 'asc';
  const isSortedDesc = sortConfig?.key === colKey && sortConfig?.direction === 'desc';

  const opsList = type === 'number' ? NUMBER_OPS : TEXT_OPS;
  const filterLabel = type === 'number' ? 'Number Filters' : 'Text Filters';
  const [showSubmenu, setShowSubmenu] = useState(false);

  return (
    <div className={`excel-filter-container ${type === 'number' ? 'numeric-th' : ''}`} ref={ref}>
      <div className="th-content" onClick={() => setIsOpen(!isOpen)}>
        <span>{title}</span>
        <ListFilter size={14} className={`filter-icon ${isActive ? 'active' : ''}`} />
      </div>
      {isOpen && (
        <div className={`excel-filter-popup popup-align-${align}`} onClick={(e) => e.stopPropagation()}>
          <div className="filter-sort-options">
             <button className={isSortedAsc ? 'active-sort' : ''} onClick={() => handleSort('asc')}>
               {type === 'number' ? 'Sort Smallest to Largest' : 'Sort A to Z'}
             </button>
             <button className={isSortedDesc ? 'active-sort' : ''} onClick={() => handleSort('desc')}>
               {type === 'number' ? 'Sort Largest to Smallest' : 'Sort Z to A'}
             </button>
          </div>

          <div className="cond-filters-section">
            <div className="cond-filters-trigger" onClick={() => setShowSubmenu(!showSubmenu)}>
              <span>{filterLabel}</span>
              <span className="arrow-right">›</span>
            </div>
            
            {showSubmenu && (
              <div className="cond-filters-flyout">
                <div className="cond-filters-controls">
                  <CustomSelect 
                    options={opsList} 
                    value={condOp} 
                    onChange={setCondOp} 
                    placeholder="Condition..." 
                  />
                  <input 
                    type={type === 'number' ? 'number' : 'text'} 
                    value={condVal} 
                    onChange={(e) => setCondVal(e.target.value)} 
                    placeholder="Value..." 
                    disabled={!condOp}
                  />
                </div>
                <div className="cond-filters-apply">
                  <button onClick={applyConditionFilter} disabled={!condOp}>Apply</button>
                  <button onClick={clearConditionFilter} className="btn-clear-cond">Clear</button>
                </div>
              </div>
            )}
          </div>

          <div className="filter-search">
            <Search size={14} className="search-icon-sm" />
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search in list..." />
          </div>
          
          <div className="filter-actions">
            <label className="filter-option-label select-all-label">
              <input 
                type="checkbox" 
                checked={isAllSelected} 
                onChange={(e) => e.target.checked ? selectAll() : clearAll()} 
              />
              <span>(Select All{search ? ' Search Results' : ''})</span>
            </label>
          </div>

          <div className="filter-options-list">
             {displayOptions.map(opt => (
                <label key={opt.value} className="filter-option-label">
                  <input 
                    type="checkbox" 
                    checked={draftIn.includes(opt.value)} 
                    onChange={(e) => handleCheckbox(opt.value, e.target.checked)} 
                  />
                  <span>{opt.label || '(Blank)'}</span>
                </label>
             ))}
          </div>

          <div className="filter-footer-actions">
            <button className="btn-ok" onClick={() => { onChange(colKey, { ...filterState, in: draftIn }); setIsOpen(false); }}>OK</button>
            <button className="btn-cancel" onClick={() => setIsOpen(false)}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
}

const FALLBACK_STOCK = [
  { id: 'SKU001-WH-North', name: 'Arduino Uno R3', code: 'SKU001', warehouse: 'WH-North', qty: 150, reorder: 50, value: 125000, levelPercent: 100, status: 'healthy' },
  { id: 'SKU002-WH-North', name: 'Raspberry Pi 4 Model B', code: 'SKU002', warehouse: 'WH-North', qty: 8, reorder: 20, value: 48000, levelPercent: 20, status: 'critical' },
  { id: 'SKU003-WH-South', name: 'ESP32 DevKit V1', code: 'SKU003', warehouse: 'WH-South', qty: 210, reorder: 40, value: 84000, levelPercent: 100, status: 'healthy' },
  { id: 'SKU004-WH-East', name: 'Servo Motor SG90', code: 'SKU004', warehouse: 'WH-East', qty: 25, reorder: 30, value: 7500, levelPercent: 35, status: 'warning' },
  { id: 'SKU005-WH-South', name: 'Ultrasonic Sensor HC-SR04', code: 'SKU005', warehouse: 'WH-South', qty: 180, reorder: 50, value: 36000, levelPercent: 100, status: 'healthy' },
  { id: 'SKU006-WH-North', name: '16x2 I2C LCD Display', code: 'SKU006', warehouse: 'WH-North', qty: 12, reorder: 25, value: 4200, levelPercent: 18, status: 'critical' },
  { id: 'SKU007-WH-West', name: '4-Channel Relay 5V', code: 'SKU007', warehouse: 'WH-West', qty: 95, reorder: 30, value: 19000, levelPercent: 95, status: 'healthy' },
  { id: 'SKU008-WH-East', name: 'PIR Motion Sensor Module', code: 'SKU008', warehouse: 'WH-East', qty: 45, reorder: 20, value: 9000, levelPercent: 75, status: 'healthy' },
  { id: 'SKU009-WH-North', name: 'OLED Display 0.96 inch', code: 'SKU009', warehouse: 'WH-North', qty: 5, reorder: 15, value: 2500, levelPercent: 12, status: 'critical' },
  { id: 'SKU010-WH-West', name: 'Stepper Motor NEMA17', code: 'SKU010', warehouse: 'WH-West', qty: 32, reorder: 30, value: 38400, levelPercent: 40, status: 'warning' },
  { id: 'SKU011-WH-South', name: 'DHT22 Temp & Humidity Sensor', code: 'SKU011', warehouse: 'WH-South', qty: 85, reorder: 25, value: 34000, levelPercent: 100, status: 'healthy' },
  { id: 'SKU012-WH-North', name: 'NodeMCU ESP8266', code: 'SKU012', warehouse: 'WH-North', qty: 130, reorder: 40, value: 45500, levelPercent: 100, status: 'healthy' },
];

// -------------------------------------------------------------
// MAIN PAGE
// -------------------------------------------------------------
export default function Inventory() {
  const [globalSearch, setGlobalSearch] = useState('');
  const [stockData, setStockData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isExportMenuOpen, setIsExportMenuOpen] = useState(false);
  
  // Modals & Action states
  const [activeModal, setActiveModal] = useState(null); // 'edit' | 'reorder' | 'details' | 'add'
  const [selectedItem, setSelectedItem] = useState(null);
  const [toastMessage, setToastMessage] = useState(null);
  const [formData, setFormData] = useState({});

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleOpenEdit = (item) => {
    setSelectedItem(item);
    setFormData({
      name: item.name,
      warehouse: item.warehouse,
      qty: item.qty,
      reorder: item.reorder,
      value: item.value,
    });
    setActiveModal('edit');
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    if (!selectedItem) return;
    const newQty = Number(formData.qty);
    const newReorder = Number(formData.reorder);
    const newStatus = newQty <= 0 ? 'critical' : newQty < newReorder ? 'critical' : newQty <= newReorder * 1.5 ? 'warning' : 'healthy';
    const fillPct = Math.min(Math.max((newQty / (newReorder * 3 || 1)) * 100, 0), 100);

    // Call backend API for permanent MariaDB / local persistence
    const res = await api.updateItem({
      code: selectedItem.code,
      warehouse: formData.warehouse || selectedItem.warehouse,
      name: formData.name,
      qty: newQty,
      reorder: newReorder,
      rate: Number(formData.value) && newQty ? Number(formData.value) / newQty : 100
    });

    setStockData(prev => prev.map(row => {
      if (row.id === selectedItem.id) {
        return {
          ...row,
          name: formData.name,
          warehouse: formData.warehouse,
          qty: newQty,
          reorder: newReorder,
          value: Number(formData.value) || row.value,
          levelPercent: fillPct,
          status: newStatus,
        };
      }
      return row;
    }));
    setActiveModal(null);
    showToast(res?.message || `Stock updated for ${formData.name}`);
  };

  const handleOpenReorder = (item) => {
    setSelectedItem(item);
    setFormData({
      reorderQty: Math.max(item.reorder * 2 - item.qty, item.reorder || 50),
      supplier: 'Apex Industrial Tech (Primary)',
      urgency: 'high',
      notes: ''
    });
    setActiveModal('reorder');
  };

  const handleSaveReorder = async (e) => {
    e.preventDefault();
    if (!selectedItem) return;
    const addedQty = Number(formData.reorderQty) || 0;

    // Call backend API to trigger ERPNext Material Request / Reorder logger
    const res = await api.createReorder({
      item_code: selectedItem.code,
      item_name: selectedItem.name,
      warehouse: selectedItem.warehouse,
      qty: addedQty,
      priority: formData.urgency || 'High',
      supplier: formData.supplier || 'Apex Industrial Tech (Primary)',
      notes: formData.notes || ''
    });

    setActiveModal(null);
    if (res?.order_id) {
      showToast(`Requisition ${res.order_id} placed! ${res.erp_synced ? '(ERPNext Synced)' : '(Logged)'}`);
    } else {
      showToast(`Purchase requisition for ${addedQty} units of ${selectedItem.name} submitted!`);
    }
  };

  const handleOpenDetails = (item) => {
    setSelectedItem(item);
    setActiveModal('details');
  };

  const handleOpenAdd = () => {
    setFormData({
      name: '',
      code: `SKU${String(stockData.length + 1).padStart(3, '0')}`,
      warehouse: 'WH-North',
      qty: 100,
      reorder: 25,
      rate: 450
    });
    setActiveModal('add');
  };

  const handleSaveAdd = async (e) => {
    e.preventDefault();
    if (!formData.name) return;
    const qty = Number(formData.qty) || 0;
    const reorder = Number(formData.reorder) || 20;
    const rate = Number(formData.rate) || 100;
    const status = qty <= 0 ? 'critical' : qty < reorder ? 'critical' : qty <= reorder * 1.5 ? 'warning' : 'healthy';
    const fillPct = Math.min(Math.max((qty / (reorder * 3 || 1)) * 100, 0), 100);

    // Call backend API for permanent MariaDB / local persistence
    const res = await api.addItem({
      code: formData.code,
      name: formData.name,
      warehouse: formData.warehouse,
      qty: qty,
      reorder: reorder,
      rate: rate
    });

    const newItem = {
      id: `${formData.code}-${formData.warehouse}-${Date.now()}`,
      name: formData.name,
      code: formData.code,
      warehouse: formData.warehouse,
      qty: qty,
      reorder: reorder,
      value: qty * rate,
      levelPercent: fillPct,
      status: status
    };

    setStockData(prev => [newItem, ...prev]);
    setActiveModal(null);
    showToast(res?.message || `New item "${formData.name}" added to inventory!`);
  };
  
  // filters: { [colKey]: { in: [], condOp: '', condVal: '', type: 'number'|'text' } }
  const [filters, setFilters] = useState({});
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  const loadData = async (refresh = false) => {
    if (refresh) setIsRefreshing(true);
    else setLoading(true);
    
    const res = await api.dashboardStock();
    if (res && res.data && res.data.length > 0) {
      const mapped = res.data.map(item => {
        const reorder = item.reorder_level || 1;
        const fillPct = Math.min(Math.max((item.qty / (reorder * 3)) * 100, 0), 100);
        return {
          id: `${item.item_code}-${item.warehouse}`,
          name: item.item_name,
          code: item.item_code,
          warehouse: (item.warehouse || '').split(' - ')[0],
          qty: Number(item.qty),
          reorder: Number(item.reorder_level) || 0,
          value: Number(item.stock_value) || 0,
          levelPercent: fillPct,
          status: item.status
        };
      });
      setStockData(mapped);
    } else {
      setStockData(prev => prev.length > 0 ? prev : FALLBACK_STOCK);
    }
    
    if (refresh) setIsRefreshing(false);
    else setLoading(false);
  };

  useEffect(() => { loadData(); }, []);

  const handleFilterChange = (colKey, newFilterState) => {
    setFilters(prev => ({ ...prev, [colKey]: newFilterState }));
  };

  const buildOptions = (key, formatter) => {
    const unique = [...new Set(stockData.map(item => item[key]))].sort((a,b) => a > b ? 1 : -1);
    return unique.map(val => ({
      value: val,
      label: formatter ? formatter(val) : String(val)
    }));
  };

  const optionsMap = useMemo(() => {
    return {
      name: buildOptions('name'),
      code: buildOptions('code'),
      warehouse: buildOptions('warehouse'),
      qty: buildOptions('qty', formatIndianNumber),
      reorder: buildOptions('reorder', formatIndianNumber),
      value: buildOptions('value', formatCurrency),
      status: buildOptions('status')
    };
  }, [stockData]);

  const filteredRows = useMemo(() => {
    // Pre-compute Sets for IN filters to avoid O(N^2) array.includes() bottleneck
    const inFilterSets = {};
    for (const [colKey, state] of Object.entries(filters)) {
      if (state.in && state.in.length > 0) {
        inFilterSets[colKey] = new Set(state.in);
      }
    }

    return stockData.filter(item => {
      // 1. Global Search
      const term = globalSearch.toLowerCase();
      if (term && !(item.name || '').toLowerCase().includes(term) && !(item.code || '').toLowerCase().includes(term)) {
        return false;
      }
      
      // 2. Column Filters
      for (const [colKey, filterState] of Object.entries(filters)) {
        const itemVal = item[colKey];
        
        // IN filter (checkboxes) using O(1) Set lookup
        if (inFilterSets[colKey]) {
          if (!inFilterSets[colKey].has(itemVal)) return false;
        }
        
        // Cond filter
        if (filterState.condOp && filterState.condVal !== '') {
          if (filterState.type === 'number') {
            const numItemVal = Number(itemVal);
            const numFilterVal = Number(filterState.condVal);
            if (!Number.isFinite(numItemVal) || !Number.isFinite(numFilterVal)) return false;
            
            switch (filterState.condOp) {
              case '==': if (numItemVal !== numFilterVal) return false; break;
              case '!=': if (numItemVal === numFilterVal) return false; break;
              case '>':  if (numItemVal <= numFilterVal) return false; break;
              case '>=': if (numItemVal < numFilterVal) return false; break;
              case '<':  if (numItemVal >= numFilterVal) return false; break;
              case '<=': if (numItemVal > numFilterVal) return false; break;
              default: break;
            }
          } else {
            const strItemVal = String(itemVal).toLowerCase();
            const strFilterVal = String(filterState.condVal).toLowerCase();
            
            switch (filterState.condOp) {
              case 'contains': if (!strItemVal.includes(strFilterVal)) return false; break;
              case 'not_contains': if (strItemVal.includes(strFilterVal)) return false; break;
              case 'starts_with': if (!strItemVal.startsWith(strFilterVal)) return false; break;
              case 'ends_with': if (!strItemVal.endsWith(strFilterVal)) return false; break;
              case 'exact': if (strItemVal !== strFilterVal) return false; break;
              default: break;
            }
          }
        }
      }
      return true;
    });
  }, [stockData, globalSearch, filters]);

  const processedRows = useMemo(() => {
    let rows = [...filteredRows];
    if (sortConfig.key) {
      rows.sort((a, b) => {
        let valA = a[sortConfig.key];
        let valB = b[sortConfig.key];
        
        if (valA === undefined || valA === null) valA = '';
        if (valB === undefined || valB === null) valB = '';
        
        if (typeof valA === 'string' && typeof valB === 'string') {
          valA = valA.toLowerCase();
          valB = valB.toLowerCase();
        }
        
        if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
        if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    return rows;
  }, [filteredRows, sortConfig]);

  const tableContainerRef = useRef(null);
  
  const rowVirtualizer = useVirtualizer({
    count: processedRows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => 50,
    overscan: 10,
  });

  const virtualItems = rowVirtualizer.getVirtualItems();
  const paddingTop = virtualItems.length > 0 ? virtualItems[0]?.start || 0 : 0;
  const paddingBottom = virtualItems.length > 0 ? rowVirtualizer.getTotalSize() - (virtualItems[virtualItems.length - 1]?.end || 0) : 0;
  const getExportData = () => {
    if (!processedRows || processedRows.length === 0) return null;
    return processedRows.map(row => ({
      'Item Name': row.name || '',
      'Code': row.code || '',
      'Warehouse': row.warehouse || '',
      'Qty': row.qty || 0,
      'Reorder Level': row.reorder || 0,
      'Value': row.value || 0,
      'Status': row.status || ''
    }));
  };

  const getFilename = (ext) => {
    const today = new Date().toISOString().split('T')[0];
    return `StockSense_Inventory_${today}.${ext}`;
  };

  const downloadFile = (content, filename, mimeType, isBinary = false) => {
    const blob = isBinary
      ? new Blob([content], { type: mimeType })
      : new Blob([content], { type: mimeType + ';charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    setIsExportMenuOpen(false);
  };

  const handleExport = (format) => {
    const data = getExportData();
    if (!data || !Array.isArray(data) || data.length === 0) {
      console.error('Export failed: no data provided');
      return;
    }

    const exportCSV = () => {
      const csv = Papa.unparse(data);
      downloadFile(csv, getFilename('csv'), 'text/csv');
    };

    const exportExcel = () => {
      const worksheet = XLSX.utils.json_to_sheet(data);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Inventory');
      XLSX.writeFile(workbook, getFilename('xlsx')); 
      setIsExportMenuOpen(false);
    };

    const exportTSV = () => {
      const tsv = Papa.unparse(data, { delimiter: '\t' });
      downloadFile(tsv, getFilename('tsv'), 'text/tab-separated-values');
    };

    const exportJSON = () => {
      const json = JSON.stringify(data, null, 2);
      downloadFile(json, getFilename('json'), 'application/json');
    };

    const exportXML = () => {
      const xmlRows = data.map(row => {
        const items = Object.entries(row).map(([key, value]) => {
          const safeKey = key.replace(/\s+/g, '');
          return `    <${safeKey}>${String(value ?? '')}</${safeKey}>`;
        }).join('\n');
        return `  <Item>\n${items}\n  </Item>`;
      }).join('\n');
      const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<Inventory>\n${xmlRows}\n</Inventory>`;
      downloadFile(xml, getFilename('xml'), 'application/xml');
    };

    const exportSQL = () => {
      const tableName = 'inventory';
      const columns = Object.keys(data[0]);
      const safeColumns = columns.map(c => c.replace(/\s+/g, '_').toLowerCase());
      const values = data.map(row =>
        `(${columns.map(col => {
          const val = row[col];
          if (val === null || val === undefined || val === '') return 'NULL';
          if (typeof val === 'number') return val;
          return `'${String(val).replace(/'/g, "''")}'`;
        }).join(', ')})`
      );
      const sql = `INSERT INTO ${tableName} (${safeColumns.join(', ')}) VALUES\n` + values.join(',\n') + ';';
      downloadFile(sql, getFilename('sql'), 'application/sql');
    };

    const exportHTML = () => {
      const columns = Object.keys(data[0]);
      const rows = data.map(row =>
        `<tr>${columns.map(col => `<td>${row[col] ?? ''}</td>`).join('')}</tr>`
      ).join('\n');
      const html = `<!DOCTYPE html>\n<html><head><meta charset="UTF-8"><title>StockSense Inventory</title></head>\n<body>\n<table border="1">\n<thead><tr>${columns.map(c => `<th>${c}</th>`).join('')}</tr></thead>\n<tbody>${rows}</tbody>\n</table>\n</body></html>`;
      downloadFile(html, getFilename('html'), 'text/html');
    };

    const exportMHTML = () => {
      const columns = Object.keys(data[0]);
      const rows = data.map(row =>
        `<tr>${columns.map(col => `<td>${row[col] ?? ''}</td>`).join('')}</tr>`
      ).join('\n');
      const boundary = '----MHTMLBoundary';
      const mhtml = `From: <Saved by StockSense>\nSubject: StockSense Inventory\nMIME-Version: 1.0\nContent-Type: multipart/related; boundary="${boundary}"\n\n--${boundary}\nContent-Type: text/html; charset="utf-8"\nContent-Transfer-Encoding: 8bit\n\n<html><body>\n<table border="1">\n<thead><tr>${columns.map(c => `<th>${c}</th>`).join('')}</tr></thead>\n<tbody>${rows}</tbody>\n</table>\n</body></html>\n\n--${boundary}--`;
      downloadFile(mhtml, getFilename('mhtml'), 'multipart/related');
    };

    const exportMarkdown = () => {
      const columns = Object.keys(data[0]);
      const separator = columns.map(() => '---').join('|');
      const mdRows = data.map(row => columns.map(col => String(row[col] ?? '')).join('|')).join('\n');
      const md = `# StockSense Inventory\n\n${columns.join('|')}\n${separator}\n${mdRows}\n`;
      downloadFile(md, getFilename('md'), 'text/markdown');
    };

    const exportText = () => {
      const columns = Object.keys(data[0]);
      const text = data.map(row =>
        columns.map(col => `${col}: ${row[col] ?? ''}`).join(' | ')
      ).join('\n');
      downloadFile(text, getFilename('txt'), 'text/plain');
    };

    const exporters = {
      csv: exportCSV,
      excel: exportExcel,
      tsv: exportTSV,
      json: exportJSON,
      xml: exportXML,
      sql: exportSQL,
      html: exportHTML,
      mhtml: exportMHTML,
      markdown: exportMarkdown,
      text: exportText,
    };

    const fn = exporters[format];
    if (fn) {
      fn();
    } else {
      console.error('Unknown export format:', format);
    }
  };

  return (
    <main className="inventory-page">
      <header className="inventory-header">
        <div className="inventory-header__copy">
          <h1>Inventory</h1>
          <p>Live stock levels across all warehouses.</p>
        </div>
        <div className="inventory-header__right">
          <div className="toolbar__left">
            <label className="search-input-wrapper">
              <Search size={16} className="search-icon" aria-hidden="true" />
              <input
                className="search-input"
                type="search"
                value={globalSearch}
                onChange={(e) => setGlobalSearch(e.target.value)}
                placeholder="Search items..."
              />
            </label>
            <span className="result-count">
              Showing {processedRows.length} of {formatIndianNumber(stockData.length)} items
            </span>
          </div>
          <div className="inventory-header__actions">
            <button className="btn-add-item" onClick={handleOpenAdd} title="Add New Item">
              <Plus size={14} />
              <span>Add Item</span>
            </button>
            <div className="live-indicator">
              <span className="live-dot"></span>
              <span>Live</span>
            </div>
            <div className="export-dropdown-wrapper">
              <button 
                className={`btn-refresh ${isExportMenuOpen ? 'active' : ''}`} 
                onClick={() => setIsExportMenuOpen(!isExportMenuOpen)} 
                title="Export Data"
              >
                <Download size={14} />
              </button>
              {isExportMenuOpen && (
                <div className="export-menu">
                  <button className="export-menu-item" onClick={() => handleExport('csv')}>Export to CSV</button>
                  <button className="export-menu-item" onClick={() => handleExport('excel')}>Export to Excel</button>
                  <button className="export-menu-item" onClick={() => handleExport('tsv')}>Export to TSV</button>
                  <button className="export-menu-item" onClick={() => handleExport('json')}>Export to JSON</button>
                  <button className="export-menu-item" onClick={() => handleExport('xml')}>Export to XML</button>
                  <button className="export-menu-item" onClick={() => handleExport('sql')}>Export to SQL</button>
                  <button className="export-menu-item" onClick={() => handleExport('html')}>Export to HTML</button>
                  <button className="export-menu-item" onClick={() => handleExport('mhtml')}>Export to MHTML</button>
                  <button className="export-menu-item" onClick={() => handleExport('markdown')}>Export to Markdown</button>
                  <button className="export-menu-item" onClick={() => handleExport('text')}>Export to Text</button>
                </div>
              )}
            </div>
            <button className="btn-refresh" onClick={() => loadData(true)} disabled={isRefreshing} title="Refresh Data">
              <RefreshCw size={14} className={isRefreshing ? 'is-spinning' : ''} />
            </button>
          </div>
        </div>
      </header>

      <section className="table-card" aria-label="Inventory table">
        <div className="table-scroll" ref={tableContainerRef} style={{ height: 'calc(100vh - 85px)', overflow: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th className="filter-th">
                  <ExcelFilter title="Item" colKey="name" type="text" options={optionsMap.name} filterState={filters.name} onChange={handleFilterChange} onSort={setSortConfig} sortConfig={sortConfig} align="left" />
                </th>
                <th className="filter-th">
                  <ExcelFilter title="Code" colKey="code" type="text" options={optionsMap.code} filterState={filters.code} onChange={handleFilterChange} onSort={setSortConfig} sortConfig={sortConfig} align="left" />
                </th>
                <th className="filter-th">
                  <ExcelFilter title="Warehouse" colKey="warehouse" type="text" options={optionsMap.warehouse} filterState={filters.warehouse} onChange={handleFilterChange} onSort={setSortConfig} sortConfig={sortConfig} />
                </th>
                <th className="filter-th">
                  <ExcelFilter title="Qty" colKey="qty" type="number" options={optionsMap.qty} filterState={filters.qty} onChange={handleFilterChange} onSort={setSortConfig} sortConfig={sortConfig} />
                </th>
                <th className="filter-th">
                  <ExcelFilter title="Reorder" colKey="reorder" type="number" options={optionsMap.reorder} filterState={filters.reorder} onChange={handleFilterChange} onSort={setSortConfig} sortConfig={sortConfig} />
                </th>
                <th className="filter-th">
                  <ExcelFilter title="Value" colKey="value" type="number" options={optionsMap.value} filterState={filters.value} onChange={handleFilterChange} onSort={setSortConfig} sortConfig={sortConfig} />
                </th>
                <th>Level</th>
                <th className="filter-th">
                  <ExcelFilter title="Status" colKey="status" type="text" options={optionsMap.status} filterState={filters.status} onChange={handleFilterChange} onSort={setSortConfig} sortConfig={sortConfig} />
                </th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <SkeletonRows />
              ) : processedRows.length === 0 ? (
                <tr className="empty-row">
                  <td colSpan="8">
                    <div className="empty-state">
                      <PackageSearch size={32} aria-hidden="true" />
                      <strong>No items match your filters</strong>
                    </div>
                  </td>
                </tr>
              ) : (
                <>
                  {paddingTop > 0 && (
                    <tr>
                      <td style={{ height: `${paddingTop}px`, padding: 0, border: 0 }} colSpan="8" />
                    </tr>
                  )}
                  {virtualItems.map((virtualRow) => {
                    const item = processedRows[virtualRow.index];
                    const qty = Number(item.qty);
                    const hasQty = Number.isFinite(qty);
                    return (
                      <tr 
                        className={`inventory-row row-status-${item.status || 'unknown'}`} 
                        key={item.id}
                        ref={rowVirtualizer.measureElement}
                        data-index={virtualRow.index}
                      >
                        <td className="item-cell">{item.name || '—'}</td>
                      <td><span className="sku-tag">{item.code || '—'}</span></td>
                      <td><span className="warehouse-pill">{item.warehouse || '—'}</span></td>
                      <td className={`numeric qty-cell ${hasQty && qty < 0 ? 'is-negative' : ''}`}>
                        {hasQty ? formatIndianNumber(qty) : '—'}
                      </td>
                      <td className="numeric reorder-cell">
                        {formatIndianNumber(item.reorder)}
                      </td>
                      <td className="numeric value-cell">
                        <span className="currency-symbol">₹</span>
                        <span>{formatCurrency(item.value)}</span>
                      </td>
                      <td><LevelBar levelPercent={item.levelPercent} status={item.status} /></td>
                      <td>
                        <div className="status-cell-content">
                          <StatusBadge status={item.status} />
                          <div className="row-actions">
                            <button className="row-action-btn" title="Edit Item" onClick={(e) => { e.stopPropagation(); handleOpenEdit(item); }}>
                              <Edit2 size={14} />
                            </button>
                            <button className="row-action-btn" title="Reorder Stock" onClick={(e) => { e.stopPropagation(); handleOpenReorder(item); }}>
                              <ShoppingCart size={14} />
                            </button>
                            <button className="row-action-btn" title="Item Details" onClick={(e) => { e.stopPropagation(); handleOpenDetails(item); }}>
                              <Eye size={14} />
                            </button>
                          </div>
                        </div>
                      </td>
                    </tr>
                    );
                  })}
                  {paddingBottom > 0 && (
                    <tr>
                      <td style={{ height: `${paddingBottom}px`, padding: 0, border: 0 }} colSpan="8" />
                    </tr>
                  )}
                </>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* Edit Item Modal */}
      {activeModal === 'edit' && selectedItem && (
        <div className="modal-backdrop" onClick={() => setActiveModal(null)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Edit Item: {selectedItem.code}</h3>
              <button className="modal-close-btn" onClick={() => setActiveModal(null)}><X size={16} /></button>
            </div>
            <form onSubmit={handleSaveEdit} className="modal-form">
              <div className="form-group">
                <label>Item Name</label>
                <input value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Warehouse</label>
                  <input value={formData.warehouse} onChange={e => setFormData({...formData, warehouse: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label>Stock Qty</label>
                  <input type="number" value={formData.qty} onChange={e => setFormData({...formData, qty: e.target.value})} required />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Reorder Point</label>
                  <input type="number" value={formData.reorder} onChange={e => setFormData({...formData, reorder: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label>Valuation (₹)</label>
                  <input type="number" value={formData.value} onChange={e => setFormData({...formData, value: e.target.value})} required />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn-primary">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Reorder Modal */}
      {activeModal === 'reorder' && selectedItem && (
        <div className="modal-backdrop" onClick={() => setActiveModal(null)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Reorder Stock: {selectedItem.name}</h3>
              <button className="modal-close-btn" onClick={() => setActiveModal(null)}><X size={16} /></button>
            </div>
            <form onSubmit={handleSaveReorder} className="modal-form">
              <div className="telemetry-card" style={{ marginBottom: 8 }}>
                <div className="label">Current Status</div>
                <div className="val" style={{ fontSize: 13, display: 'flex', gap: 12 }}>
                  <span>Stock: <strong>{selectedItem.qty}</strong></span>
                  <span>Threshold: <strong>{selectedItem.reorder}</strong></span>
                  <span>Warehouse: <strong>{selectedItem.warehouse}</strong></span>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Order Qty (Units)</label>
                  <input type="number" min="1" value={formData.reorderQty} onChange={e => setFormData({...formData, reorderQty: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label>Priority</label>
                  <select value={formData.urgency} onChange={e => setFormData({...formData, urgency: e.target.value})}>
                    <option value="normal">Normal</option>
                    <option value="high">High Priority</option>
                    <option value="urgent">Urgent Restock</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Preferred Supplier</label>
                <input value={formData.supplier} onChange={e => setFormData({...formData, supplier: e.target.value})} />
              </div>
              <div className="form-group">
                <label>Notes / Justification</label>
                <input placeholder="Reason for reorder..." value={formData.notes} onChange={e => setFormData({...formData, notes: e.target.value})} />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn-primary">Submit Purchase Order</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Item Details Modal */}
      {activeModal === 'details' && selectedItem && (
        <div className="modal-backdrop" onClick={() => setActiveModal(null)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3>{selectedItem.name}</h3>
                <span style={{ fontSize: 12, color: 'var(--text-tertiary)', fontFamily: 'JetBrains Mono, monospace' }}>{selectedItem.code}</span>
              </div>
              <button className="modal-close-btn" onClick={() => setActiveModal(null)}><X size={16} /></button>
            </div>
            <div className="item-telemetry-grid">
              <div className="telemetry-card">
                <div className="label">Current Stock</div>
                <div className="val">{formatIndianNumber(selectedItem.qty)}</div>
              </div>
              <div className="telemetry-card">
                <div className="label">Reorder Level</div>
                <div className="val">{formatIndianNumber(selectedItem.reorder)}</div>
              </div>
              <div className="telemetry-card">
                <div className="label">Stock Valuation</div>
                <div className="val">₹{formatCurrency(selectedItem.value)}</div>
              </div>
              <div className="telemetry-card">
                <div className="label">Warehouse</div>
                <div className="val" style={{ fontSize: 14 }}>{selectedItem.warehouse}</div>
              </div>
            </div>
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: 12 }}>
                <span style={{ color: 'var(--text-secondary)' }}>Capacity Level</span>
                <span style={{ fontWeight: 600 }}>{Math.round(selectedItem.levelPercent)}%</span>
              </div>
              <LevelBar levelPercent={selectedItem.levelPercent} status={selectedItem.status} />
            </div>
            <div className="modal-footer">
              <button type="button" className="btn-secondary" onClick={() => setActiveModal(null)}>Close</button>
              <button type="button" className="btn-primary" onClick={() => { setActiveModal(null); handleOpenReorder(selectedItem); }}>
                Initiate Reorder
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add New Item Modal */}
      {activeModal === 'add' && (
        <div className="modal-backdrop" onClick={() => setActiveModal(null)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add New Inventory Item</h3>
              <button className="modal-close-btn" onClick={() => setActiveModal(null)}><X size={16} /></button>
            </div>
            <form onSubmit={handleSaveAdd} className="modal-form">
              <div className="form-group">
                <label>Item Name</label>
                <input placeholder="e.g. Raspberry Pi Zero 2 W" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Item Code / SKU</label>
                  <input value={formData.code} onChange={e => setFormData({...formData, code: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label>Warehouse</label>
                  <select value={formData.warehouse} onChange={e => setFormData({...formData, warehouse: e.target.value})}>
                    <option value="WH-North">WH-North</option>
                    <option value="WH-South">WH-South</option>
                    <option value="WH-East">WH-East</option>
                    <option value="WH-West">WH-West</option>
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Initial Qty</label>
                  <input type="number" min="0" value={formData.qty} onChange={e => setFormData({...formData, qty: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label>Reorder Point</label>
                  <input type="number" min="1" value={formData.reorder} onChange={e => setFormData({...formData, reorder: e.target.value})} required />
                </div>
              </div>
              <div className="form-group">
                <label>Unit Valuation Rate (₹)</label>
                <input type="number" min="0" value={formData.rate} onChange={e => setFormData({...formData, rate: e.target.value})} required />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn-primary">Create Item</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toastMessage && (
        <div className="stocksense-toast">
          <Check size={16} style={{ color: '#2DD4BF' }} />
          <span>{toastMessage}</span>
        </div>
      )}
    </main>
  );
}
