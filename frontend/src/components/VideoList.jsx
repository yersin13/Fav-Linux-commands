export default function VideoList({ videos, selectedIds, processingIds, onToggle }) {
  return (
    <div className="video-list">
      {videos.map((video) => {
        const isSelected = selectedIds.has(video.id)
        const isProcessing = processingIds.has(video.id)
        return (
          <div
            key={video.id}
            className={`video-card${isSelected ? ' selected' : ''}${isProcessing ? ' processing' : ''}`}
            onClick={() => onToggle(video.id)}
          >
            <div className="video-card-checkbox">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => onToggle(video.id)}
                onClick={(e) => e.stopPropagation()}
              />
            </div>
            <div className="video-card-info">
              <span className="video-title">{video.title}</span>
              <span className="video-id">{video.id}</span>
            </div>
            {isProcessing && <span className="processing-badge">processing...</span>}
          </div>
        )
      })}
    </div>
  )
}
