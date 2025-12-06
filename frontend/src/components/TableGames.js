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
            <TableCell>Game Title</TableCell>
            <TableCell align="right">Release Date</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {tableData.map((row, index) => (
            <TableRow key={index} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
              <TableCell component="th" scope="row">
                <Link 
                  href={`https://store.steampowered.com/search/?term=${encodeURIComponent(row.product_id)}`} 
                  target="_blank" 
                  rel="noopener"
                  underline="hover"
                  sx={{ display: 'flex', alignItems: 'center', color: 'white', fontWeight: 500 }}
                >
                  {row.product_id} 
                  <LaunchIcon sx={{ marginLeft: 1, fontSize: 14, opacity: 0.7 }}/>
                </Link>
              </TableCell>
              <TableCell align="right" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                {row.title}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default TableGames;