// Function to start research
async function startResearch() {
    const query = document.getElementById('query').value;
    const depth = document.getElementById('depth').value;
    
    if (!query) {
        alert('Please enter a research query');
        return;
    }

    // Show loading state
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');

    try {
        const response = await fetch('/research', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                queries: [query],
                max_depth: parseInt(depth)
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Hide loading and show results
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('results').classList.remove('hidden');

            // Update synthesis
            document.getElementById('synthesis').innerHTML = data.results.synthesis;

            // Update sources
            const sourcesHtml = data.results.research.map(result => `
                <div class="card">
                    <h4 class="font-bold">${result.title}</h4>
                    <p>${result.summary}</p>
                    <a href="${result.url}" target="_blank" class="text-blue-400 hover:text-blue-300">Read more</a>
                </div>
            `).join('');
            document.getElementById('sources').innerHTML = sourcesHtml;

            // Create knowledge graph
            createGraph(data.results.research);
        } else {
            throw new Error(data.detail || 'Research failed');
        }
    } catch (error) {
        document.getElementById('loading').classList.add('hidden');
        alert('Error: ' + error.message);
    }
}

// Function to create knowledge graph
function createGraph(research) {
    const graphDiv = document.getElementById('graph');
    graphDiv.innerHTML = ''; // Clear previous graph

    // Create a simple force-directed graph using D3
    const width = graphDiv.clientWidth;
    const height = graphDiv.clientHeight;

    const svg = d3.select('#graph')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    // Create nodes and links from research data
    const nodes = research.map((item, index) => ({
        id: index,
        title: item.title,
        radius: 30
    }));

    const links = [];
    for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
            links.push({
                source: i,
                target: j,
                value: 1
            });
        }
    }

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id))
        .force('charge', d3.forceManyBody().strength(-100))
        .force('center', d3.forceCenter(width / 2, height / 2));

    // Add links
    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .enter()
        .append('line')
        .style('stroke', 'rgba(255, 255, 255, 0.2)');

    // Add nodes
    const node = svg.append('g')
        .selectAll('circle')
        .data(nodes)
        .enter()
        .append('circle')
        .attr('r', d => d.radius)
        .style('fill', 'rgba(107, 140, 255, 0.3)')
        .style('stroke', 'rgba(255, 255, 255, 0.5)')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    // Add node titles
    node.append('title')
        .text(d => d.title);

    // Update positions
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
    });

    // Drag functions
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
} 