import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Team from './pages/Team.jsx'
import PlayerDetail from './pages/PlayerDetail.jsx'

function App() {
  return (
    <Router>
      <header>
        {/* <Navbar /> */}
      </header>
      <main>
        <Routes>
            <Route path="/" element={<Team/>}/>
            <Route path="/team/:teamid" element={<Team />} />
            <Route path="/player/:playerid" element={<PlayerDetail />} />
        </Routes>
      </main>
      <footer>
      </footer>
    </Router>
  )
}

export default App


export const ItemTypes = {
    PLAYER: 'Player',
    'C':'C',
    '1B':'1B',
    '2B':'2B',
    '3B':'3B',
    'SS':'SS',
    'LF':'LF',
    'CF':'CF',
    'RF':'RF',
    'SP':'SP',
    'RP':'RP'
  }