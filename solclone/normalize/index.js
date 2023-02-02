const fs = require('fs');
const path = require('path');

const parser = require('@solidity-parser/parser');

function decamlizeToWords(identifier) {
    return identifier.split(/[$_]/).reduce((words, chunk) => {
        if(chunk.length === 0) {
            return words;
        }
        if(/^[A-Z]+$/.test(chunk)) {
            words.push(chunk);
        } else {
            const cooker = /I?ERC\d*|ABI|API|BTC|DS|ETH|ID|URI/g;
            const cookedChunk = chunk.replace(cooker, word => {
                return word.charAt(0) + word.substring(1).toLowerCase();
            });
            words.push(...cookedChunk.split(/(?=[A-Z])/));
        }
        return words;
    }, []);
}

function normalize(tokens) {
    return tokens.reduce((normalizedTokens, token) => {
        switch(token.type) {
        case 'COMMENT':
        case 'LINE_COMMENT':
            break;
        case 'HexLiteralFragment': // hex'...' / hex"..."
        case 'HexNumber':
        case 'Numeric':
        case 'StringLiteralFragment':
            normalizedTokens.push(token.type);
            break;
        case 'Identifier':
            if(/^(.)\1*$/.test(token.value)) {
                normalizedTokens.push('SimpleIdentifier');
            } else {
                normalizedTokens.push(...decamlizeToWords(token.value));
            }
            break;
        default:
            normalizedTokens.push(token.value);
        }
        return normalizedTokens;
    }, []);
}

const [,, outfile, ...infiles] = process.argv;
const fout = fs.createWriteStream(outfile, { flags: 'a' });

infiles.forEach(file => {
    const addr = path.basename(file, '.sol');
    const code = fs.readFileSync(file, 'utf8');
    try {
        const ast = parser.parse(code, { range: true });
        ast.children.forEach(child => {
            if(child.type === 'ContractDefinition') {
                const contract = child.name;
                fout.write(`${addr} ${contract}`);
                // tokenize
                const [start, end] = child.range;
                const tokens = parser.tokenize(code.substring(start, end + 1));
                // normalize
                const normalizedTokens = normalize(tokens);
                normalizedTokens.forEach(token => {
                    fout.write(` ${token.toLowerCase()}`);
                });
                fout.write('\n');
            }
        });
    } catch(e) {
        if(e instanceof parser.ParserError) {
            // TODO
        }
        console.error(file, e);
    }
});

fout.end();
