import React, {useState} from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Cookies from 'js-cookie'
import { cn } from "@/lib/utils"

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import { Separator } from "@/components/ui/separator"

import { ScrollArea } from "@/components/ui/scroll-area"
import Team from './pages/Team.jsx'
import PlayerDetail from './pages/PlayerDetail.jsx'
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'
import LineupCard from '@/components/Lineup.jsx'
function App() {
  // const layout = Cookies.get("react-resizable-panels:layout")
  // const collapsed = Cookies.get("react-resizable-panels:collapsed")

  const defaultLayout =  [265, 440, 655]
  // const defaultCollapsed = collapsed ? collapsed[0] : false
  // const navCollapsedSize = 4
  const [isCollapsed, setIsCollapsed] = useState(false)
  return (
    <Router>
      <header>
        <div className="container flex flex-col items-start justify-between space-y-2 py-4 px-4 sm:flex-row sm:items-center sm:space-y-0 md:h-16">
          <h2 className="text-lg font-semibold"><a href="/">ballgame [alpha]</a></h2>
        </div>
        <Separator/>
      </header>
      <main className="pt-8 pl-4 pr-4 border">
      <DndProvider backend={HTML5Backend}>
      <ResizablePanelGroup
        direction="horizontal"
        onLayout={(sizes) => {
         Cookies.set(`react-resizable-panels:layout`,`${JSON.stringify(
            sizes
          )}`)
        }}
        className="h-full max-h-[100vh] items-stretch"
      >
        <ResizablePanel
          defaultSize={defaultLayout[0]}
          // collapsedSize={navCollapsedSize}
          // collapsible={true}
          minSize={15}
          maxSize={20}
          // onCollapse={(collapsed) => {
          //   setIsCollapsed(collapsed)
          //   Cookies.set(`react-resizable-panels:collapsed`,`${JSON.stringify(
          //     collapsed
          //   )}`)
          // }}
          className={`border-r-2 ${cn(isCollapsed && "min-w-[50px] transition-all duration-300 ease-in-out")}`}
        >
          <ScrollArea className="h-100" direction="vertical">
        <LineupCard team={"TST"}/>
        </ScrollArea>
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel defaultSize={defaultLayout[1]} minSize={30} className="">
          <div className="m-auto w-auto px-4">
            <ScrollArea className="h-100" direction="vertical">
        <Routes>
            <Route path="/" element={<Team/>}/>
            <Route path="/team/:teamid" element={<Team />} />
            <Route path="/player/:playerid" element={<PlayerDetail />} />
        </Routes>
        </ScrollArea>
        </div>
        </ResizablePanel>
        </ResizablePanelGroup>
        </DndProvider>
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