# New Modern Frontend - User Guide

## Overview

The new frontend is a **modern, professional UI** inspired by the Framer Aset template design system. It features:

✨ **Dark Theme** - Professional, easy on the eyes
🎨 **Modern Design** - Clean gradients, smooth animations
📱 **Fully Responsive** - Works on all devices
🚀 **Complete RAG Integration** - Semantic search and AI Q&A
⚡ **Real-time Updates** - Live statistics and notifications

## Files

- **`index_new.html`** - Main HTML structure
- **`styles_new.css`** - Modern CSS with design system
- **`app_new.js`** - Complete JavaScript functionality

## Quick Start

### 1. Enable the New Frontend

Replace the old frontend files or create symbolic links:

```bash
cd frontend

# Backup old files
mv index.html index_old.html
mv styles.css styles_old.css
mv app.js app_old.js

# Use new files
mv index_new.html index.html
mv styles_new.css styles.css
mv app_new.js app.js
```

### 2. Start the Backend

```bash
cd ../backend
source venv/bin/activate
python manage.py runserver
```

### 3. Serve the Frontend

```bash
cd ../frontend
python -m http.server 3000
```

### 4. Open in Browser

Navigate to: **http://localhost:3000**

## Features

### 🎯 Hero Section

- **Eye-catching title** with gradient text
- **Real-time statistics** showing total files, chunks, and indexed files
- **Quick actions** to jump to upload or search

### 📤 File Upload

**Single File Upload**
- Drag & drop or click to browse
- Optional comment for better AI categorization
- Automatic indexing after upload
- Beautiful result display with AI analysis

**Batch Upload**
- Upload multiple files at once
- Shared comment for all files
- Progress tracking
- Success/failure breakdown

### 🔍 Semantic Search

**Search Features:**
- Natural language queries
- Filter by file type (documents, images, videos, etc.)
- Adjustable result limit
- Real-time search results with relevance scoring

**Search Results Display:**
- File name and type
- Relevant text chunks
- Chunk position indicators
- Quick reindex button

### 🤖 RAG Q&A

**Ask Questions:**
- Ask anything about your documents
- AI generates comprehensive answers
- Source citations included
- Context-aware responses

**Example Questions:**
- "What are the main topics in my documents?"
- "Summarize the key findings from the reports"
- "What does the contract say about payment terms?"

### 📊 JSON Data Storage

**Smart Storage:**
- Paste JSON data directly
- AI decides: SQL or NoSQL
- Confidence score shown
- Complete schema generation

**Schema Display:**
- **SQL**: Full CREATE TABLE statement with column details
- **NoSQL**: MongoDB document structure
- AI reasoning explanation
- Storage statistics

### 📈 Analytics Dashboard

**Real-time Metrics:**
- Total files stored
- Indexed chunks for search
- Searchable files count
- Refresh button for latest data

## Design System

### Color Palette

```css
Primary Background:   #0a0a0a
Secondary Background: #111111
Card Background:      #161616

Accent Primary:       #6366f1 (Indigo)
Accent Secondary:     #8b5cf6 (Purple)
Success Color:        #10b981 (Green)
Error Color:          #ef4444 (Red)
```

### Typography

- **Font Family**: Inter (Google Fonts)
- **Headings**: 700 weight, 1.1 line-height
- **Body Text**: 400 weight, 1.6 line-height
- **Code**: Courier New, monospace

### Spacing System

```css
XS:  0.25rem (4px)
SM:  0.5rem  (8px)
MD:  1rem    (16px)
LG:  1.5rem  (24px)
XL:  2rem    (32px)
2XL: 3rem    (48px)
3XL: 4rem    (64px)
```

### Components

**Buttons:**
- Primary: Gradient background with hover animation
- Secondary: Bordered with subtle hover effect
- Text: Minimal style for secondary actions

**Cards:**
- Gradient background (dark to darker)
- Border with subtle glow on hover
- Smooth lift animation
- Rounded corners (12px)

**Forms:**
- Dark backgrounds
- Focused state with accent color
- Smooth transitions
- Accessible labels

**Toasts:**
- Auto-dismissing notifications
- Color-coded by type (success, error, warning)
- Slide-in animation
- Positioned top-right

## Animations

### Subtle Interactions

- **Button Hover**: Lift effect (-2px transform)
- **Card Hover**: Slight lift with shadow
- **Toast Slide-in**: Smooth entrance from right
- **Status Dot**: Pulsing animation

### Transitions

- **Fast**: 150ms for hover states
- **Base**: 200ms for most interactions
- **Slow**: 300ms for complex animations

### Loading States

- **Overlay**: Full-screen with backdrop blur
- **Spinner**: Rotating border animation
- **Text**: "Processing..." message

## Responsive Design

### Breakpoints

**Mobile (< 768px):**
- Navigation links hidden
- Stacked hero stats
- Single column grids
- Full-width buttons

**Tablet (768px - 1024px):**
- 2-column grids
- Condensed spacing
- Adjusted font sizes

**Desktop (> 1024px):**
- Full layout with max-width container
- 3-column stat grids
- Optimal spacing

## API Integration

### Endpoints Used

```javascript
// File Upload
POST /api/storage/upload/file/
POST /api/storage/upload/batch/

// JSON Upload
POST /api/storage/upload/json/

// RAG Operations
POST /api/storage/rag/search/
POST /api/storage/rag/query/
POST /api/storage/rag/index/<file_id>/

// Statistics
GET  /api/storage/media-files/statistics/
GET  /api/storage/rag/stats/

// Health Check
GET  /api/storage/health/
```

### Error Handling

- Network errors caught and displayed
- User-friendly error messages
- Automatic retry suggestions
- Toast notifications for all errors

## User Experience Features

### Drag & Drop

- Visual feedback with border color change
- "drag-over" class for active state
- Support for single and multiple files
- Prevention of default browser behavior

### Real-time Feedback

- Loading overlay during operations
- Toast notifications for success/error
- Auto-updating statistics
- Progress indicators

### Keyboard Navigation

- Tab through form elements
- Enter to submit forms
- Escape to close modals
- Accessible focus states

## Browser Compatibility

✅ **Chrome/Edge**: Full support
✅ **Firefox**: Full support
✅ **Safari**: Full support (webkit prefixes included)
⚠️ **IE11**: Not supported (modern CSS required)

## Performance Optimizations

### CSS

- Single stylesheet (no additional requests)
- CSS custom properties for theming
- Minimal specificity for fast parsing
- Hardware-accelerated animations (transform)

### JavaScript

- Event delegation where applicable
- Debounced search (if needed)
- Lazy loading for results
- Minimal DOM manipulation

### Assets

- Google Fonts with preconnect
- SVG icons (inline, no requests)
- No images (pure CSS design)
- Optimized animation keyframes

## Customization

### Changing Colors

Edit CSS custom properties in `styles_new.css`:

```css
:root {
    --accent-primary: #your-color;
    --accent-secondary: #your-color;
}
```

### Adding Sections

1. Add HTML structure in `index_new.html`
2. Add styles in `styles_new.css`
3. Add functionality in `app_new.js`

### Modifying Animations

Edit animation duration in CSS:

```css
:root {
    --transition-fast: 150ms;
    --transition-base: 200ms;
    --transition-slow: 300ms;
}
```

## Accessibility

### ARIA Labels

- Buttons have descriptive labels
- Form inputs have associated labels
- Icon buttons include text alternatives
- Status indicators have semantic meaning

### Keyboard Support

- All interactive elements focusable
- Logical tab order
- Visible focus indicators
- Form submission with Enter key

### Color Contrast

- Text meets WCAG AA standards
- Sufficient contrast on all backgrounds
- Multiple visual indicators (not just color)

## Troubleshooting

### Stats Not Loading

**Problem**: Stats show "0" or "-"
**Solution**: Check backend is running and CORS is enabled

```bash
# Verify backend
curl http://localhost:8000/api/storage/health/
```

### Upload Not Working

**Problem**: Files don't upload
**Solution**: Check FormData and backend logs

```javascript
// Check browser console for errors
// Verify API endpoint is correct
```

### Search Returns No Results

**Problem**: Search shows no results
**Solution**: Ensure documents are indexed

```bash
# Check indexed files
curl http://localhost:8000/api/storage/rag/stats/
```

### Styling Issues

**Problem**: Colors or fonts not loading
**Solution**: Clear browser cache and check Google Fonts

```bash
# Hard refresh: Ctrl+Shift+R (Linux/Windows)
# or Cmd+Shift+R (Mac)
```

## Development Tips

### Live Reload

Use a development server with live reload:

```bash
# Using Python
python -m http.server 3000

# Using Node.js (if available)
npx http-server -p 3000
```

### Debugging

```javascript
// Enable console logging in app_new.js
console.log('API Response:', data);
```

### Testing

1. **Upload**: Try different file types
2. **Search**: Test various queries
3. **JSON**: Test SQL vs NoSQL decisions
4. **Mobile**: Use browser DevTools responsive mode

## Deployment

### Static Hosting

The frontend is pure HTML/CSS/JS and can be hosted anywhere:

**Options:**
- Netlify
- Vercel
- GitHub Pages
- Any static host

**Steps:**
1. Update API_BASE in `app_new.js` to production URL
2. Upload files to hosting service
3. Configure CORS on backend

### Production Backend

Update the API base URL:

```javascript
// app_new.js
const API_BASE = 'https://your-production-api.com/api/storage';
```

### HTTPS

Ensure both frontend and backend use HTTPS in production:

```javascript
const API_BASE = 'https://api.example.com/api/storage';
```

## Future Enhancements

Potential additions:

- [ ] User authentication UI
- [ ] File preview modal
- [ ] Advanced filters for search
- [ ] Batch indexing UI
- [ ] Analytics charts
- [ ] Dark/light theme toggle
- [ ] Export search results
- [ ] File management (delete, rename)

## Credits

**Design Inspiration**: Framer Aset Template
**Fonts**: Google Fonts (Inter)
**Icons**: Custom SVG
**Framework**: Vanilla JavaScript

---

**Ready to use!** Start the backend, serve the frontend, and enjoy your modern intelligent storage system! 🚀
