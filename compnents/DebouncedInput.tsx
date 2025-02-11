import Input, { InputProps } from '@mui/joy/Input';
import Typography from '@mui/joy/Typography';
import { useEffect, useRef, useState } from 'react';
import Box from '@mui/joy/Box';

type DebounceProps = {
  handleDebounce: (value: string) => void;
  debounceTimeout: number;
};

export default function DebounceInput(props: InputProps & DebounceProps) {
  const { handleDebounce, debounceTimeout,value, ...other } = props;
  const [inputValue, setInputValue] = useState(value);
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value;
    setInputValue(newValue);
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      handleDebounce(newValue);
    }, debounceTimeout);
  };

  useEffect(() => {
    setInputValue(value);
  }, [value]);

  return <Input {...other} value={inputValue} onChange={handleChange} />;
}

function DebouncedInput() {
  const [debouncedValue, setDebouncedValue] = useState('');
  const handleDebounce = (value: string) => {
    setDebouncedValue(value);
  };
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <DebounceInput
        placeholder="Type in here…"
        debounceTimeout={1000}
        handleDebounce={handleDebounce}
      />
      <Typography>Debounced input: {debouncedValue}</Typography>
    </Box>
  );
}
