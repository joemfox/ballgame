import React, {useEffect,useState} from 'react'
import axios from 'axios'
import { BrowserRouter as Router, Routes, Route, Link, useParams } from 'react-router-dom'
import Cookies from "universal-cookie"
import { cn } from "@/lib/utils"

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import { Separator } from "@/components/ui/separator"
import { Input } from "@/components/ui/input"

import { ScrollArea } from "@/components/ui/scroll-area"
import Team from './pages/Team.jsx'
import Players from './pages/Players.jsx'
import PlayerDetail from './pages/PlayerDetail.jsx'
import Standings from './pages/Standings.jsx'
import Draft from './pages/Draft.jsx'
import Settings from './pages/Settings.jsx'
import Transactions from './pages/Transactions.jsx'
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'
import LineupCard from '@/components/Lineup.jsx'
import ThemeToggle from '@/components/ThemeToggle.jsx'

// Apply saved theme before first render
;(function () {
  const stored = localStorage.getItem('theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  if (stored === 'dark' || (!stored && prefersDark)) {
    document.documentElement.classList.add('dark')
  }
})()

function TeamRoute({ team, rosterVersion, onRosterChange }) {
  const { teamid } = useParams()
  return <Team team={team} viewTeam={teamid} rosterVersion={rosterVersion} onRosterChange={onRosterChange} />
}

const cookies = new Cookies();
function App() {
  const [loginState, setLoginState] = useState({
    username: "",
    password: "",
    error: "",
    isAuthenticated: false,
  })
  const [team, setTeam] = useState(null)
  const [isAdmin, setIsAdmin] = useState(false)
  const [isLoggingIn, setIsLoggingIn] = useState(false)
  const [rosterVersion, setRosterVersion] = useState(0)
  const onRosterChange = () => setRosterVersion(v => v + 1)
  const [draftMode, setDraftMode] = useState(false)

  function handleDraftPick(fgId, _slot, onSuccess) {
    axios.post('/api/draft/pick', { player_fg_id: fgId })
      .then(() => { onRosterChange(); onSuccess() })
      .catch(err => console.error('Draft pick failed:', err))
  }

  useEffect(() => {
    getSession()
  },[])

  function getWhoami() {
    fetch("/api/whoami/", { credentials: "same-origin" })
      .then((res) => res.json())
      .then((data) => { if (data.team) setTeam(data.team); if (data.is_staff) setIsAdmin(true) })
      .catch((err) => { console.log(err) })
  }

  function getSession(){
    fetch("/api/session/", {
      credentials: "same-origin",
    })
    .then((res) => res.json())
    .then((data) => {
      if (data.isAuthenticated) {
        setLoginState({isAuthenticated: true});
        getWhoami();
      } else {
        setLoginState({isAuthenticated: false});
      }
    })
    .catch((err) => {
      console.log(err);
    });
  }

  function isResponseOk(response) {
    if (response.status >= 200 && response.status <= 299) {
      return response.json();
    } else {
      throw Error(response.statusText);
    }
  }

  function login(event){
    event.preventDefault();
    setIsLoggingIn(true);
    fetch(`/login/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": cookies.get("csrftoken"),
      },
      credentials: "same-origin",
      body: JSON.stringify({username: loginState.username, password: loginState.password}),
    })
    .then(isResponseOk)
    .then((data) => {
      setLoginState({isAuthenticated: true, username: "", password: "", error: ""});
      getWhoami();
    })
    .catch((err) => {
      setLoginState({error: "Wrong username or password."});
    })
    .finally(() => {
      setIsLoggingIn(false)
    });
  }

  const handlePasswordChange = (event) => {
    setLoginState(f => ({...f, password: event.target.value}));
  }

  const handleUserNameChange = (event) => {
    setLoginState(f => ({...f, username: event.target.value}));
  }

  function logout(){
    fetch("/api/logout/", {
      credentials: "same-origin",
    })
    .then(isResponseOk)
    .then((data) => {
      console.log(data);
      setLoginState({isAuthenticated: false});
    })
    .catch((err) => {
      console.log(err);
    });
  };
const [isCollapsed, setIsCollapsed] = useState(false)
  const [rosterOpen, setRosterOpen] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  // Detect mobile (< 768px), reactive to resize
  const [isMobile, setIsMobile] = useState(() => window.innerWidth < 768)
  useEffect(() => {
    const mq = window.matchMedia('(max-width: 767px)')
    const handler = (e) => setIsMobile(e.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])

  if(!loginState.isAuthenticated){
    return (
      <div className="min-h-screen flex items-center justify-center relative">
        <div className="absolute top-4 right-4"><ThemeToggle /></div>
        <div className="w-full max-w-sm p-8 border rounded-lg shadow-sm bg-card text-card-foreground">
          <h1 className="text-2xl font-semibold geist-mono mb-1">sombrero.quest</h1>
          <p className="text-sm text-muted-foreground mb-6">Sign in to your account</p>
          <form onSubmit={login} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium mb-1">Username</label>
              <Input type="text" id="username" name="username" onChange={handleUserNameChange} />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-1">Password</label>
              <Input type="password" id="password" name="password" onChange={handlePasswordChange} />
              {loginState.error && <p className="text-sm text-red-500 mt-1">{loginState.error}</p>}
            </div>
            <button type="submit" disabled={isLoggingIn}
              className="w-full bg-primary text-primary-foreground rounded-md px-4 py-2 text-sm font-medium hover:bg-primary/90 disabled:opacity-50">
              {isLoggingIn ? 'Signing in…' : 'Sign in'}
            </button>
          </form>
        </div>
      </div>
    )
  }
  const routes = (
    <Routes>
      <Route path="/" element={<Team team={team} rosterVersion={rosterVersion} onRosterChange={onRosterChange}/>}/>
      <Route path="/players" element={<Players team={team} rosterVersion={rosterVersion} onRosterChange={onRosterChange}/>} />
      <Route path="/team/:teamid" element={<TeamRoute team={team} rosterVersion={rosterVersion} onRosterChange={onRosterChange}/>} />
      <Route path="/player/:playerid" element={<PlayerDetail />} />
      <Route path="/standings" element={<Standings />} />
      <Route path="/draft" element={<Draft team={team} isAdmin={isAdmin} onRosterChange={onRosterChange} setDraftMode={setDraftMode} />} />
      <Route path="/settings" element={<Settings onTeamUpdate={(abbr) => setTeam(abbr)} />} />
      <Route path="/transactions" element={<Transactions />} />
    </Routes>
  )

  return (
    <Router>
      <header>
        <div className="flex items-center justify-between py-3 px-4 h-14 w-full">
          <h2 className="text-lg font-semibold geist-mono tracking-tight"><a href="/">sombrero.quest</a></h2>
          {/* Desktop nav */}
          <nav className="hidden sm:flex items-center gap-4 text-sm">
            <Link to="/">My Team</Link>
            <Link to="/players">Players</Link>
            <Link to="/standings">Standings</Link>
            <Link to="/transactions">Transactions</Link>
            <Link to="/draft">Draft</Link>
            <Link to="/settings">Settings</Link>
            <ThemeToggle />
          </nav>
          {/* Mobile nav toggle */}
          <div className="flex sm:hidden items-center gap-2">
            <ThemeToggle />
            <button onClick={() => setMenuOpen(o => !o)} className="p-2 rounded-md hover:bg-muted" aria-label="Menu">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                {menuOpen
                  ? <path fillRule="evenodd" clipRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" />
                  : <path fillRule="evenodd" clipRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" />
                }
              </svg>
            </button>
          </div>
        </div>
        {/* Mobile dropdown menu */}
        {menuOpen && (
          <nav className="sm:hidden border-t px-4 py-2 flex flex-col gap-1 text-sm bg-background">
            <Link to="/" onClick={() => setMenuOpen(false)} className="py-2 hover:text-foreground/70">My Team</Link>
            <Link to="/players" onClick={() => setMenuOpen(false)} className="py-2 hover:text-foreground/70">Players</Link>
            <Link to="/standings" onClick={() => setMenuOpen(false)} className="py-2 hover:text-foreground/70">Standings</Link>
            <Link to="/transactions" onClick={() => setMenuOpen(false)} className="py-2 hover:text-foreground/70">Transactions</Link>
            <Link to="/draft" onClick={() => setMenuOpen(false)} className="py-2 hover:text-foreground/70">Draft</Link>
            <Link to="/settings" onClick={() => setMenuOpen(false)} className="py-2 hover:text-foreground/70">Settings</Link>
          </nav>
        )}
        <Separator/>
      </header>
      <DndProvider backend={HTML5Backend}>
        {isMobile ? (
          <main>
            {/* Drawer */}
            <div
              style={{ maxHeight: rosterOpen ? '70vh' : '0', transition: 'max-height 0.3s ease-in-out' }}
              className="overflow-hidden border-b"
            >
              <ScrollArea className="h-[70vh]">
                <LineupCard team={team} rosterVersion={rosterVersion} onRosterChange={onRosterChange} onDraftPick={draftMode ? handleDraftPick : undefined}/>
              </ScrollArea>
            </div>
            {/* Folder tab */}
            <div className="flex justify-center">
              <button
                onClick={() => setRosterOpen(o => !o)}
                className="px-6 py-0.5 text-xs font-medium text-muted-foreground bg-muted border border-t-0 rounded-b-md leading-5"
              >
                {rosterOpen ? '▲ roster' : '▼ roster'}
              </button>
            </div>
            <div className="px-4 pt-4 overflow-y-auto h-[calc(100vh-56px)]">
              {routes}
            </div>
          </main>
        ) : (
          <main className="pl-4 pr-4 border">
            <ResizablePanelGroup
              direction="horizontal"
              className="h-full max-h-[100vh] items-stretch"
            >
              <ResizablePanel
                defaultSize={25}
                minSize={15}
                maxSize={40}
                className={`border-r-2  pt-4 ${cn(isCollapsed && "min-w-[50px] transition-all duration-300 ease-in-out")}`}
              >
                <ScrollArea className="h-[calc(100vh-80px)]">
                  <LineupCard team={team} rosterVersion={rosterVersion} onRosterChange={onRosterChange} onDraftPick={draftMode ? handleDraftPick : undefined}/>
                </ScrollArea>
              </ResizablePanel>
              <ResizableHandle />
              <ResizablePanel defaultSize={75} minSize={60}>
                <div className="m-auto  pt-4 w-auto px-4 h-[calc(100vh-80px)] overflow-y-auto">
                  {routes}
                </div>
              </ResizablePanel>
            </ResizablePanelGroup>
          </main>
        )}
      </DndProvider>
      <footer>
        <div className="w-full h-16"></div>
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