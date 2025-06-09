import { useState } from 'react'
import FileUpload from './components/FileUpload'
import SearchBar from './components/SearchBar'
import TranscriptionList from './components/TranscriptionList'
import AllTranscriptionButton from './components/AllTranscriptionButton'
import './App.css'

function App() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handleTranscriptionsLoaded = (transcriptions: any[]) => {
    console.log('Transcriptions loaded in App:', transcriptions);
    // You can handle the loaded transcriptions here if needed
    // For example, you might want to update some state or trigger a refresh
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Audio Transcription App</h1>
      <div className="mb-8">
        <FileUpload />
      </div>
      <hr />

      <div className="mb-8 space-y-6"> {/* Adds consistent spacing between all children */}
        <h2 className="text-2xl font-bold">Search Transcriptions by name</h2>
        <SearchBar onSearch={handleSearch} />
        <TranscriptionList searchQuery={searchQuery} />
      </div>
      <hr />

      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4">See all transcripts</h2>
        <AllTranscriptionButton onTranscriptionsLoaded={handleTranscriptionsLoaded} />
      </div>
    </div>
  )
}

export default App
