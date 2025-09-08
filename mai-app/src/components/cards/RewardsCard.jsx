// Future events data
const futureEvents = [
  { title: 'New Model Launch', date: '2025-09-15', description: 'Attend the launch event for the new electric SUV.' },
  { title: 'Sales Training Seminar', date: '2025-09-22', description: 'Participate in advanced sales techniques workshop.' },
  { title: 'Customer Appreciation Day', date: '2025-10-01', description: 'Engage with top customers and build relationships.' },
  { title: 'Test Drive Marathon', date: '2025-10-10', description: 'Host a test drive event for potential buyers.' },
  { title: 'Quarterly Sales Review', date: '2025-10-20', description: 'Review and discuss sales performance with the team.' },
];

export const FutureEventsCard = () => (
  <Card sx={{ minWidth: 250, mb: 2 }}>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        Upcoming Events
      </Typography>
      <List dense>
        {futureEvents.map((event, idx) => (
          <ListItem key={idx} alignItems="flex-start">
            <ListItemText
              primary={event.title + ' - ' + event.date}
              secondary={event.description}
            />
          </ListItem>
        ))}
      </List>
    </CardContent>
  </Card>
);
// Side quests data
const sideQuests = [
  { action: 'Test drive a new model', xp: 150 },
  { action: 'Organize a car care workshop', xp: 250 },
  { action: 'Create a video review of a car', xp: 300 },
  { action: 'Host a Q&A session about EVs', xp: 200 },
  { action: 'Write a blog post on car maintenance', xp: 180 },
  { action: 'Share a customer success story', xp: 120 },
];

import { useMemo } from 'react';

export const SideQuestsCard = () => {
  // Pick 3 random quests for this render
  const quests = useMemo(() => {
    const shuffled = [...sideQuests].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, 3);
  }, []);
  const [checked, setChecked] = useState(Array(quests.length).fill(false));

  const handleToggle = idx => {
    setChecked(prev => prev.map((v, i) => (i === idx ? !v : v)));
  };

  return (
    <Card sx={{ minWidth: 250, mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Side Quests
        </Typography>
        <List dense>
          {quests.map((quest, idx) => (
            <ListItem key={idx} secondaryAction={
              <Checkbox
                edge="end"
                checked={checked[idx]}
                onChange={() => handleToggle(idx)}
                inputProps={{ 'aria-label': `Mark ${quest.action} as complete` }}
              />
            }>
              <ListItemText
                primary={quest.action}
                secondary={`+${quest.xp} XP`}
                sx={checked[idx] ? { textDecoration: 'line-through', color: 'text.disabled' } : {}}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};
import React from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemText, Checkbox } from '@mui/material';
import { useState } from 'react';

const dailyRewards = [
  { action: 'One car sold', xp: 500 },
  { action: 'Positive customer feedback', xp: 200 },
  { action: 'Help a teammate', xp: 100 },
];

const monthlyRewards = [
  { action: 'Five cars sold', xp: 3000 },
  { action: 'Achieve monthly sales target', xp: 2000 },
];

export const DailyRewardsCard = () => {
  const [checked, setChecked] = useState(Array(dailyRewards.length).fill(false));

  const handleToggle = idx => {
    setChecked(prev => prev.map((v, i) => (i === idx ? !v : v)));
  };

  return (
    <Card sx={{ minWidth: 250, mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Daily Rewards
        </Typography>
        <List dense>
          {dailyRewards.map((reward, idx) => (
            <ListItem key={idx} secondaryAction={
              <Checkbox
                edge="end"
                checked={checked[idx]}
                onChange={() => handleToggle(idx)}
                inputProps={{ 'aria-label': `Mark ${reward.action} as complete` }}
              />
            }>
              <ListItemText
                primary={reward.action}
                secondary={`+${reward.xp} XP`}
                sx={checked[idx] ? { textDecoration: 'line-through', color: 'text.disabled' } : {}}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export const MonthlyRewardsCard = () => {
  const [checked, setChecked] = useState(Array(monthlyRewards.length).fill(false));

  const handleToggle = idx => {
    setChecked(prev => prev.map((v, i) => (i === idx ? !v : v)));
  };

  return (
    <Card sx={{ minWidth: 250, mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Monthly Rewards
        </Typography>
        <List dense>
          {monthlyRewards.map((reward, idx) => (
            <ListItem key={idx} secondaryAction={
              <Checkbox
                edge="end"
                checked={checked[idx]}
                onChange={() => handleToggle(idx)}
                inputProps={{ 'aria-label': `Mark ${reward.action} as complete` }}
              />
            }>
              <ListItemText
                primary={reward.action}
                secondary={`+${reward.xp} XP`}
                sx={checked[idx] ? { textDecoration: 'line-through', color: 'text.disabled' } : {}}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};
