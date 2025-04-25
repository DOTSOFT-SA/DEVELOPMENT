import React, { useState } from "react";
import { TextField, IconButton, InputAdornment } from "@mui/material";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";

const ExpandableTextField = ({ label, value, onChange, error, placeholder }) => {
    const [expanded, setExpanded] = useState(false);

    const handleToggleExpand = () => {
        setExpanded((prev) => !prev);
    };

    return (
        <TextField
            label={label}
            value={value}
            onChange={onChange}
            error={error}
            placeholder={placeholder}
            size="small"
            sx={{
                width: expanded ? "200px" : "115px",
                transition: "width 0.3s",
            }}
            InputProps={{
                endAdornment: value && value.toString().length > 10 ? (
                    <InputAdornment position="end">
                        <IconButton onClick={handleToggleExpand} edge="end">
                            <KeyboardArrowRightIcon
                                sx={{
                                    transform: expanded ? "rotate(90deg)" : "rotate(0)",
                                    transition: "transform 0.3s",
                                    fontSize: 16
                                }}
                            />
                        </IconButton>
                    </InputAdornment>
                ) : null,
            }}
        />
    );
};

export default ExpandableTextField;
