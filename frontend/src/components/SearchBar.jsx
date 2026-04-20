export default function SearchBar({ value, onChange }) {
  return (
    <div className="search-bar">
      <span className="search-icon">/</span>
      <input
        type="text"
        className="search-input"
        placeholder="Search command, technique, MITRE tag, or transcript..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      {value && (
        <button className="search-clear" onClick={() => onChange('')}>x</button>
      )}
    </div>
  )
}
