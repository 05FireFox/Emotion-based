import React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Link from '@mui/material/Link';
import LaunchIcon from '@mui/icons-material/Launch';

function TableGames(props) {
  const { tableData } = props;

  return (
    <TableContainer sx={{ marginTop: 2, maxHeight: 400, overflowY: 'auto' }}>
      <Table stickyHeader aria-label="recommendation table">
        <TableHead>
          <TableRow>
            {/* Updated Header: Game Title on the left */}
            <TableCell>Game Title</TableCell>
            {/* Updated Header: Game ID on the right */}
            <TableCell align="right">Game ID</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {tableData.map((row, index) => (
            <TableRow key={index} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
              <TableCell component="th" scope="row">
                {/* Column 1: Displaying the Game Title with the Link */}
                <Link 
                  href={`https://store.steampowered.com/search/?term=${encodeURIComponent(row.title)}`} 
                  target="_blank" 
                  rel="noopener"
                  underline="hover"
                  sx={{ display: 'flex', alignItems: 'center', color: 'white', fontWeight: 500 }}
                >
                  {row.title} 
                  <LaunchIcon sx={{ marginLeft: 1, fontSize: 14, opacity: 0.7 }}/>
                </Link>
              </TableCell>
              {/* Column 2: Displaying the Game ID (product_id) */}
              <TableCell align="right" sx={{ color: 'rgba(255,255,255,0.7)', fontFamily: 'monospace' }}>
                {row.product_id}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default TableGames;