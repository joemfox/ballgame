import { useState, useEffect } from 'react'
import axios from 'axios'

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import StatlineTable from '@/components/StatlineTable.jsx'

const SLOT_POSITIONS = {
  lineup_C: 'C', lineup_1B: '1B', lineup_2B: '2B', lineup_SS: 'SS',
  lineup_3B: '3B', lineup_LF: 'LF', lineup_CF: 'CF', lineup_RF: 'RF',
  lineup_SP1: 'SP', lineup_SP2: 'SP', lineup_SP3: 'SP', lineup_SP4: 'SP', lineup_SP5: 'SP',
  lineup_RP1: 'RP', lineup_RP2: 'RP', lineup_RP3: 'RP',
}

export default function Team({ team, rosterVersion = 0, onRosterChange }) {
  const [openPositions, setOpenPositions] = useState([])
  const [activeTab, setActiveTab] = useState('hit')

  useEffect(() => {
    if (!team) return
    axios.get('/api/lineup', { params: { team } })
      .then(res => {
        const lineup = res.data
        const open = []
        for (const [slot, pos] of Object.entries(SLOT_POSITIONS)) {
          if (!lineup[slot]) open.push(pos)
        }
        // OF players are eligible for any open outfield slot
        if (['LF', 'CF', 'RF'].some(p => open.includes(p))) open.push('OF')
        // IF/IN players are eligible for any open infield slot (2B, SS, 3B)
        if (['2B', 'SS', '3B'].some(p => open.includes(p))) { open.push('IF'); open.push('IN') }
        setOpenPositions([...new Set(open)])
      })
      .catch(() => setOpenPositions([]))
  }, [team, rosterVersion])

  return (
    <Tabs defaultValue="hit" onValueChange={setActiveTab}>
      <TabsList>
        <TabsTrigger value="hit">Hitters</TabsTrigger>
        <TabsTrigger value="pitch">Pitchers</TabsTrigger>
      </TabsList>
      <TabsContent value="hit">
        {activeTab === 'hit' && <StatlineTable
          type="hit"
          team={team}
          openPositions={openPositions}
          rosterVersion={rosterVersion}
          onRosterChange={onRosterChange}
        />}
      </TabsContent>
      <TabsContent value="pitch">
        {activeTab === 'pitch' && <StatlineTable
          type="pitch"
          team={team}
          openPositions={openPositions}
          rosterVersion={rosterVersion}
          onRosterChange={onRosterChange}
        />}
      </TabsContent>
    </Tabs>
  )
}
